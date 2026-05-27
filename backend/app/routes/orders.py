from fastapi import APIRouter, HTTPException, Query
from app.services.supabase import get_supabase
from app.models.schemas import OrderCreate, OrderUpdate
from typing import Optional

router = APIRouter()


@router.get("/")
def list_orders(
    user_id: str = Query(...),
    role: str = Query(...),
    status: Optional[str] = None,
):
    supabase = get_supabase()
    query = supabase.select("repair_orders", "*")

    if role == "student":
        query = query.eq("student_id", user_id)
    elif role == "worker":
        query = query.eq("worker_id", user_id)

    if status:
        query = query.eq("status", status)

    result = query.order("created_at", asc=False).execute()
    orders = result.data or []
    return _enrich_orders(orders, supabase)


@router.get("/{order_id}")
def get_order(order_id: str):
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
    return result[0] if result else {}


@router.patch("/{order_id}")
def update_order(order_id: str, data: OrderUpdate):
    supabase = get_supabase()
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    result = supabase.update("repair_orders", updates, {"id": f"eq.{order_id}"})
    return result[0] if result else {}


@router.delete("/{order_id}")
def cancel_order(order_id: str):
    supabase = get_supabase()
    supabase.update("repair_orders", {"status": "cancelled"}, {"id": f"eq.{order_id}"})
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
