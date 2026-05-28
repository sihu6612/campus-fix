-- 修复：status_logs.operator_id 允许为空，service_role 调用时无用户上下文
-- 在 Supabase SQL Editor 中执行：https://supabase.com/dashboard/project/rgtvzpwbwikjbamyoahs/sql/new

-- 1. 允许 operator_id 为 NULL
ALTER TABLE status_logs ALTER COLUMN operator_id DROP NOT NULL;

-- 2. 更新触发器：auth.uid() 为 NULL 时回退到师傅/学生 ID
CREATE OR REPLACE FUNCTION log_status_change()
RETURNS trigger AS $$
BEGIN
  IF old.status IS DISTINCT FROM new.status THEN
    INSERT INTO status_logs (order_id, from_status, to_status, operator_id, note)
    VALUES (new.id, old.status, new.status,
      COALESCE(auth.uid(), new.worker_id, new.student_id),
      CASE
        WHEN new.status = 'assigned' THEN '已分配师傅'
        WHEN new.status = 'in_progress' THEN '师傅开始维修'
        WHEN new.status = 'awaiting_confirmation' THEN '维修完成，等待确认'
        WHEN new.status = 'completed' THEN '已确认完成'
        WHEN new.status = 'cancelled' THEN '已取消'
        ELSE '状态更新'
      END
    );
  END IF;
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
