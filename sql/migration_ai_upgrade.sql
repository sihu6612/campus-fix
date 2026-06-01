-- AI 智能升级迁移：紧急度评分 + 工人匹配 + 路径规划
-- 在 Supabase SQL Editor 中执行

-- 1. repair_orders 新增紧急度评分
alter table repair_orders add column if not exists urgency_score int default 0;

-- 2. repair_orders 新增坐标（地理编码用）
alter table repair_orders add column if not exists lat float;
alter table repair_orders add column if not exists lng float;

-- 3. profiles 新增工人匹配相关字段
alter table profiles add column if not exists skills text[] default '{}';
alter table profiles add column if not exists current_load int default 0;
alter table profiles add column if not exists lat float;
alter table profiles add column if not exists lng float;
alter table profiles add column if not exists is_available boolean default true;

-- 4. 紧急度排序索引
create index if not exists idx_orders_urgency on repair_orders(urgency_score desc);
