-- 校修通 CampusFix 数据库 Schema
-- 在 Supabase SQL Editor 中执行

-- 1. 允许前端查询的自定义声明（不强制 RLS 但表有 policy）
-- 2. 扩展
create extension if not exists "uuid-ossp";

-- ============================================
-- 用户资料表（关联 Supabase Auth）
-- ============================================
create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  role text not null check (role in ('student', 'worker', 'admin')) default 'student',
  display_name text not null default '',
  phone text default '',
  avatar_url text default '',
  worker_type text default null,  -- 师傅工种，如 电工/水工/木工...
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 新用户注册时自动创建 profile
create or replace function handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, display_name, role)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'display_name', '用户'),
    coalesce(new.raw_user_meta_data ->> 'role', 'student')
  );
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure handle_new_user();

-- ============================================
-- 维修工单表
-- ============================================
create table if not exists repair_orders (
  id uuid primary key default uuid_generate_v4(),
  student_id uuid not null references profiles(id),
  worker_id uuid references profiles(id) default null,
  category text not null default '',           -- 大类：电路/供水/家具/空调/网络/墙面/锁具/卫生/其它
  location text not null default '',            -- 具体位置
  description text not null default '',         -- 问题描述
  image_urls text[] default '{}',              -- 图片 URL 数组
  ai_analysis jsonb default '{}',              -- AI 图片分析结果
  suggested_parts text[] default '{}',         -- AI 建议配件
  complexity text check (complexity in ('simple', 'medium', 'complex')) default 'simple',
  status text not null check (
    status in ('pending', 'assigned', 'in_progress', 'awaiting_confirmation', 'completed', 'cancelled')
  ) default 'pending',
  urgency text not null check (urgency in ('normal', 'urgent')) default 'normal',
  rating int check (rating >= 1 and rating <= 5) default null,
  review text default '',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- ============================================
-- 工单消息表（聊天）
-- ============================================
create table if not exists repair_messages (
  id uuid primary key default uuid_generate_v4(),
  order_id uuid not null references repair_orders(id) on delete cascade,
  sender_id uuid not null references profiles(id),
  content text not null default '',
  image_url text default null,
  created_at timestamptz default now()
);

-- ============================================
-- 状态变更日志表
-- ============================================
create table if not exists status_logs (
  id uuid primary key default uuid_generate_v4(),
  order_id uuid not null references repair_orders(id) on delete cascade,
  from_status text,
  to_status text not null,
  operator_id uuid references profiles(id) default null,  -- nullable: 服务端 service_role 无用户上下文
  note text default '',
  created_at timestamptz default now()
);

-- ============================================
-- 索引
-- ============================================
create index if not exists idx_orders_student on repair_orders(student_id);
create index if not exists idx_orders_worker on repair_orders(worker_id);
create index if not exists idx_orders_status on repair_orders(status);
create index if not exists idx_messages_order on repair_messages(order_id);
create index if not exists idx_logs_order on status_logs(order_id);

-- ============================================
-- RLS 策略
-- ============================================
alter table profiles enable row level security;
alter table repair_orders enable row level security;
alter table repair_messages enable row level security;
alter table status_logs enable row level security;

-- profiles: 用户可读所有（需要知道师傅和物业信息），仅自己可改
drop policy if exists "profiles_select" on profiles;
create policy "profiles_select" on profiles for select using (true);
drop policy if exists "profiles_update_self" on profiles;
create policy "profiles_update_self" on profiles for update using (auth.uid() = id);

-- repair_orders: 学生看自己的，师傅看已分配的，物业看全部
drop policy if exists "orders_select" on repair_orders;
create policy "orders_select" on repair_orders for select using (
  auth.uid() = student_id
  or auth.uid() = worker_id
  or exists (select 1 from profiles where id = auth.uid() and role = 'admin')
);
drop policy if exists "orders_insert" on repair_orders;
create policy "orders_insert" on repair_orders for insert with check (auth.uid() = student_id);
drop policy if exists "orders_update" on repair_orders;
create policy "orders_update" on repair_orders for update using (
  auth.uid() = student_id
  or auth.uid() = worker_id
  or exists (select 1 from profiles where id = auth.uid() and role = 'admin')
);

-- repair_messages: 工单参与者可读可写
drop policy if exists "messages_select" on repair_messages;
create policy "messages_select" on repair_messages for select using (
  exists (
    select 1 from repair_orders
    where id = repair_messages.order_id
    and (student_id = auth.uid() or worker_id = auth.uid()
         or exists (select 1 from profiles where id = auth.uid() and role = 'admin'))
  )
);
drop policy if exists "messages_insert" on repair_messages;
create policy "messages_insert" on repair_messages for insert with check (
  auth.uid() = sender_id
);

-- status_logs: 工单参与者可读
drop policy if exists "logs_select" on status_logs;
create policy "logs_select" on status_logs for select using (
  exists (
    select 1 from repair_orders
    where id = status_logs.order_id
    and (student_id = auth.uid() or worker_id = auth.uid()
         or exists (select 1 from profiles where id = auth.uid() and role = 'admin'))
  )
);
drop policy if exists "logs_insert" on status_logs;
create policy "logs_insert" on status_logs for insert with check (auth.uid() = operator_id);

-- ============================================
-- updated_at 自动更新触发器
-- ============================================
create or replace function update_timestamp()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_profiles_updated on profiles;
create trigger trg_profiles_updated
  before update on profiles for each row execute procedure update_timestamp();

drop trigger if exists trg_orders_updated on repair_orders;
create trigger trg_orders_updated
  before update on repair_orders for each row execute procedure update_timestamp();

-- ============================================
-- 状态变更自动写日志触发器
-- ============================================
create or replace function log_status_change()
returns trigger as $$
begin
  if old.status is distinct from new.status then
    insert into status_logs (order_id, from_status, to_status, operator_id, note)
    values (new.id, old.status, new.status,
      coalesce(auth.uid(), new.worker_id, new.student_id),  -- service_role 调用时 auth.uid() 为 null，回退到师傅/学生 ID
      case
        when new.status = 'assigned' then '已分配师傅'
        when new.status = 'in_progress' then '师傅开始维修'
        when new.status = 'awaiting_confirmation' then '维修完成，等待确认'
        when new.status = 'completed' then '已确认完成'
        when new.status = 'cancelled' then '已取消'
        else '状态更新'
      end
    );
  end if;
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists trg_order_status_change on repair_orders;
create trigger trg_order_status_change
  before update on repair_orders for each row execute procedure log_status_change();
