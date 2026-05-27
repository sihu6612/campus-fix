"""通过 Supabase PgBouncer 连接池初始化数据库"""
import sys
import os

SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
if not SERVICE_KEY:
    print("请设置 SUPABASE_SERVICE_KEY 环境变量")
    print("或手动在 Supabase SQL Editor 中执行 sql/schema.sql")
    sys.exit(1)

DB_URL = f"postgresql://postgres:{SERVICE_KEY}@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"

sql_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql", "schema.sql")
with open(sql_path, "r", encoding="utf-8") as f:
    sql = f.read()

print(f"连接池: aws-0-ap-northeast-1.pooler.supabase.com:6543")

try:
    import psycopg2
except ImportError:
    os.system(f'"{sys.executable}" -m pip install psycopg2-binary -q')
    import psycopg2

# 逐条 SQL 分割
statements = []
current = []
for line in sql.split("\n"):
    stripped = line.strip()
    if not stripped or stripped.startswith("--"):
        continue
    current.append(line)
    if stripped.endswith(";"):
        stmt = "\n".join(current).strip()
        if stmt:
            statements.append(stmt)
        current = []

try:
    conn = psycopg2.connect(DB_URL + "?sslmode=require")
    cur = conn.cursor()
    total = len(statements)
    for i, stmt in enumerate(statements):
        try:
            cur.execute(stmt)
            conn.commit()
            # 截取前40字符作为描述
            desc = stmt.split("\n")[0].strip()[:50]
            print(f"  [{i+1}/{total}] OK  {desc}...")
        except Exception as e:
            err = str(e)
            if any(kw in err.lower() for kw in ["already exists", "duplicate", "depends on"]):
                print(f"  [{i+1}/{total}] SKIP (already exists)")
            else:
                print(f"  [{i+1}/{total}] ERR: {err[:100]}")
            conn.rollback()
    cur.close()
    conn.close()
    print("\n  数据库初始化完成!")
except Exception as e:
    print(f"\n  连接失败: {e}")
    print(f"\n  请手动在 Supabase SQL Editor 执行: {sql_path}")
    print(f"  https://supabase.com/dashboard/project/rgtvzpwbwikjbamyoahs")
    sys.exit(1)
