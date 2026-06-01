from fastapi import APIRouter, HTTPException, Query
from app.services.supabase import get_supabase
from app.models.schemas import OrderCreate, OrderUpdate, BatchUpdate
from typing import Optional
import re

router = APIRouter()

UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


def _validate_uuid(value: str, name: str = "id"):
    if not UUID_RE.match(value):
        raise HTTPException(status_code=400, detail=f"无效的 {name} 格式")



@router.get("/")
def list_orders(
    user_id: str = Query(...),
    role: str = Query(...),
    status: Optional[str] = None,
    category: Optional[str] = None,
    class_name: Optional[str] = None,
):
    _validate_uuid(user_id, "user_id")
    supabase = get_supabase()
    query = supabase.select("repair_orders", "*")

    if role == "student":
        query = query.eq("student_id", user_id)
    elif role == "worker":
        query = query.eq("worker_id", user_id)
    elif role == "counselor":
        counselor = supabase.select("profiles", "class_name").eq("id", user_id).single().execute()
        cn = class_name or (counselor.data or {}).get("class_name", "")
        if cn:
            students = supabase.select("profiles", "id").eq("class_name", cn).eq("role", "student").execute()
            student_ids = [s["id"] for s in (students.data or [])]
            if student_ids:
                query = query.in_("student_id", student_ids)
            else:
                return []
        else:
            return []
    elif role == "admin" and class_name:
        students = supabase.select("profiles", "id").eq("class_name", class_name).eq("role", "student").execute()
        student_ids = [s["id"] for s in (students.data or [])]
        if student_ids:
            query = query.in_("student_id", student_ids)
        else:
            return []

    if category:
        query = query.eq("category", category)
    if status:
        query = query.eq("status", status)

    result = query.order("created_at", asc=False).execute()
    orders = result.data or []
    return _enrich_orders(orders, supabase)


@router.get("/{order_id}")
def get_order(order_id: str):
    _validate_uuid(order_id, "order_id")
    supabase = get_supabase()
    result = supabase.select("repair_orders", "*").eq("id", order_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="工单不存在")
    return _enrich_orders([result.data], supabase)[0]


@router.post("/")
def create_order(data: OrderCreate, student_id: str = Query(...)):
    supabase = get_supabase()
    order = {
        "student_id": student_id,
        "category": data.category,
        "location": data.location,
        "description": data.description,
        "image_urls": data.image_urls,
        "urgency": data.urgency,
        "ai_analysis": data.ai_analysis,
        "suggested_parts": data.suggested_parts,
        "complexity": data.complexity,
    }
    result = supabase.insert("repair_orders", order)
    if not result:
        raise HTTPException(status_code=500, detail="工单创建失败，请重试")
    return result[0]


@router.patch("/{order_id}")
def update_order(order_id: str, data: OrderUpdate):
    supabase = get_supabase()
    updates = {k: v for k, v in data.model_dump(mode="json").items() if v is not None}
    result = supabase.update("repair_orders", updates, {"id": f"eq.{order_id}"})
    if not result:
        raise HTTPException(status_code=500, detail="工单更新失败，请重试")
    return result[0]


@router.delete("/{order_id}")
def cancel_order(order_id: str, hard: bool = Query(False)):
    supabase = get_supabase()
    if hard:
        # 硬删除：先清关联消息和日志，再删工单
        supabase.delete("repair_messages", {"order_id": f"eq.{order_id}"})
        supabase.delete("status_logs", {"order_id": f"eq.{order_id}"})
        supabase.delete("repair_orders", {"id": f"eq.{order_id}"})
    else:
        supabase.update("repair_orders", {"status": "cancelled"}, {"id": f"eq.{order_id}"})
    return {"ok": True}


@router.post("/batch")
def batch_update_orders(data: BatchUpdate):
    supabase = get_supabase()
    updates = {k: v for k, v in data.updates.items() if v is not None}
    for oid in data.order_ids:
        supabase.update("repair_orders", updates, {"id": f"eq.{oid}"})
    return {"ok": True, "count": len(data.order_ids)}


# 自定义类别（内存存储，重启后恢复为内置类别）
_CUSTOM_CATEGORIES = []


@router.get("/categories")
def list_categories():
    base = ["电路/灯具", "供水/管道", "家具/门窗", "空调/电器", "网络/弱电", "墙面/渗水", "锁具/五金", "卫生/下水", "其它"]
    return {"categories": base + _CUSTOM_CATEGORIES}


@router.post("/categories")
def add_category(data: dict):
    name = data.get("name", "").strip()
    if name and name not in _CUSTOM_CATEGORIES:
        _CUSTOM_CATEGORIES.append(name)
    return {"ok": True}


@router.delete("/categories/{name}")
def remove_category(name: str):
    global _CUSTOM_CATEGORIES
    _CUSTOM_CATEGORIES = [c for c in _CUSTOM_CATEGORIES if c != name]
    return {"ok": True}


def _enrich_orders(orders: list, supabase):
    """填充学生名和师傅名"""
    if not orders:
        return []
    student_ids = {o["student_id"] for o in orders}
    worker_ids = {o["worker_id"] for o in orders if o.get("worker_id")}

    all_ids = list(student_ids | worker_ids)
    profiles = {}
    if all_ids:
        try:
            res = supabase.select("profiles", "id,display_name").in_("id", all_ids).execute()
            for p in (res.data or []):
                profiles[p["id"]] = p["display_name"]
        except Exception:
            pass

    for o in orders:
        o["student_name"] = profiles.get(o["student_id"], "")
        o["worker_name"] = profiles.get(o.get("worker_id"), "")
    return orders
