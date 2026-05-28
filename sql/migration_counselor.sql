-- 辅导员角色迁移
-- 在 Supabase SQL Editor 中执行

-- 1. 添加 class_name 字段
alter table profiles add column if not exists class_name text default '';

-- 2. 更新 role check 约束，加入 counselor
alter table profiles drop constraint if exists profiles_role_check;
alter table profiles add constraint profiles_role_check
  check (role in ('student', 'worker', 'admin', 'counselor'));

-- 3. 更新新用户触发器
create or replace function handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, display_name, role, class_name)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'display_name', '用户'),
    coalesce(new.raw_user_meta_data ->> 'role', 'student'),
    coalesce(new.raw_user_meta_data ->> 'class_name', '')
  );
  return new;
end;
$$ language plpgsql security definer;

-- 4. RLS — profiles 保持公开可读
-- profiles_update_self 保持不变

-- 5. RLS — repair_orders 加入 counselor 支持
drop policy if exists "orders_select" on repair_orders;
create policy "orders_select" on repair_orders for select using (
  auth.uid() = student_id
  or auth.uid() = worker_id
  or exists (select 1 from profiles where id = auth.uid() and role = 'admin')
  or exists (
    select 1 from profiles counselor
    where counselor.id = auth.uid() and counselor.role = 'counselor'
    and exists (
      select 1 from profiles student
      where student.id = repair_orders.student_id
      and student.class_name = counselor.class_name
      and counselor.class_name <> ''
    )
  )
);

-- orders_insert 不变（学生才能创建）
-- orders_update 加入 counselor（但实际 counselor 只能聊天不能改工单）

-- 6. RLS — repair_messages 加入 counselor 支持
drop policy if exists "messages_select" on repair_messages;
create policy "messages_select" on repair_messages for select using (
  exists (
    select 1 from repair_orders
    where id = repair_messages.order_id
    and (
      student_id = auth.uid()
      or worker_id = auth.uid()
      or exists (select 1 from profiles where id = auth.uid() and role = 'admin')
      or exists (
        select 1 from profiles counselor
        where counselor.id = auth.uid() and counselor.role = 'counselor'
        and exists (
          select 1 from profiles student
          where student.id = repair_orders.student_id
          and student.class_name = counselor.class_name
          and counselor.class_name <> ''
        )
      )
    )
  )
);

-- messages_insert 不变（参与者都可以发消息，但 counselor 需要通过后端API）

-- 7. RLS — status_logs 加入 counselor 支持
drop policy if exists "logs_select" on status_logs;
create policy "logs_select" on status_logs for select using (
  exists (
    select 1 from repair_orders
    where id = status_logs.order_id
    and (
      student_id = auth.uid()
      or worker_id = auth.uid()
      or exists (select 1 from profiles where id = auth.uid() and role = 'admin')
      or exists (
        select 1 from profiles counselor
        where counselor.id = auth.uid() and counselor.role = 'counselor'
        and exists (
          select 1 from profiles student
          where student.id = repair_orders.student_id
          and student.class_name = counselor.class_name
          and counselor.class_name <> ''
        )
      )
    )
  )
);

-- 8. 索引
create index if not exists idx_profiles_class on profiles(class_name);
