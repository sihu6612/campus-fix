from fastapi import APIRouter, Query
from app.services.supabase import get_supabase
from app.models.schemas import MessageCreate

router = APIRouter()


@router.get("/{order_id}")
def list_messages(order_id: str):
    supabase = get_supabase()
    result = supabase.select("repair_messages", "*").eq("order_id", order_id).order("created_at", asc=True).execute()
    msgs = result.data or []

    sender_ids = {m["sender_id"] for m in msgs}
    profiles = {}
    if sender_ids:
        try:
            res = supabase.select("profiles", "id,display_name").in_("id", list(sender_ids)).execute()
            for p in (res.data or []):
                profiles[p["id"]] = p["display_name"]
        except Exception:
            pass

    for m in msgs:
        m["sender_name"] = profiles.get(m["sender_id"], "")
    return msgs


@router.post("/")
def send_message(data: MessageCreate, sender_id: str = Query(...)):
    supabase = get_supabase()
    msg = {
        "order_id": str(data.order_id),
        "sender_id": sender_id,
        "content": data.content,
        "image_url": data.image_url,
    }
    result = supabase.insert("repair_messages", msg)
    return result[0] if result else {}


@router.get("/{order_id}/logs")
def list_logs(order_id: str):
    supabase = get_supabase()
    result = supabase.select("status_logs", "*").eq("order_id", order_id).order("created_at", asc=True).execute()
    logs = result.data or []

    op_ids = {l["operator_id"] for l in logs}
    profiles = {}
    if op_ids:
        try:
            res = supabase.select("profiles", "id,display_name").in_("id", list(op_ids)).execute()
            for p in (res.data or []):
                profiles[p["id"]] = p["display_name"]
        except Exception:
            pass

    for l in logs:
        l["operator_name"] = profiles.get(l["operator_id"], "")
    return logs
