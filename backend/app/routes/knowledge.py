from fastapi import APIRouter, Query
from app.services.supabase import get_supabase

router = APIRouter()


@router.get("/search")
def search_knowledge(
    q: str = Query(default="", description="搜索关键词"),
    category: str = Query(default="", description="限定分类"),
    limit: int = Query(default=5, le=10),
):
    """搜索已完成的工单知识库，返回匹配的维修案例"""
    supabase = get_supabase()
    query = supabase.select("repair_orders", "id,category,description,solution,suggested_parts,worker_id,created_at")

    # 只看已完成的工单
    query = query.eq("status", "completed")

    # 分类筛选
    if category:
        query = query.eq("category", category)

    result = query.order("created_at", asc=False).limit(limit * 3).execute()
    orders = result.data or []

    # 关键词匹配过滤
    if q:
        kw = q.lower()
        orders = [
            o for o in orders
            if kw in (o.get("description", "") + o.get("solution", "")).lower()
        ]

    orders = orders[:limit]

    # 填充师傅名
    worker_ids = {o["worker_id"] for o in orders if o.get("worker_id")}
    profiles = {}
    if worker_ids:
        try:
            res = supabase.select("profiles", "id,display_name").in_("id", list(worker_ids)).execute()
            for p in (res.data or []):
                profiles[p["id"]] = p["display_name"]
        except Exception:
            pass

    results = []
    for o in orders:
        results.append({
            "id": o["id"],
            "category": o.get("category", ""),
            "description": o.get("description", ""),
            "solution": o.get("solution", ""),
            "suggested_parts": o.get("suggested_parts") or [],
            "worker_name": profiles.get(o.get("worker_id"), ""),
            "created_at": o.get("created_at", ""),
        })

    return results
