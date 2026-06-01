-- 知识库迁移：给工单表添加 solution 字段
-- 师傅完工时填写维修方案，沉淀为可检索的知识库

alter table repair_orders add column if not exists solution text default '';

-- 为知识库搜索建索引
create index if not exists idx_orders_completed_cat on repair_orders(status, category) where status = 'completed';
