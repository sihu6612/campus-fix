from fastapi import APIRouter
from app.models.schemas import AgentChatRequest, AgentChatResponse
from app.services.agent import chat_with_agent, MOCK_REPLY
from app.services.supabase import get_supabase

router = APIRouter()


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(req: AgentChatRequest):
    order_info = None
    if req.order_id:
        try:
            supabase = get_supabase()
            result = supabase.select("repair_orders", "*").eq("id", req.order_id).single().execute()
            if result.data:
                o = result.data
                order_info = {
                    "category": o.get("category", ""),
                    "location": o.get("location", ""),
                    "status": o.get("status", ""),
                    "description": o.get("description", ""),
                }
        except Exception:
            pass

    user_orders = None
    if req.user_id:
        try:
            supabase = get_supabase()
            q = supabase.select("repair_orders", "id,category,location,description,status,urgency,created_at").order("created_at", asc=False).limit(10)
            if req.role == "student":
                q = q.eq("student_id", req.user_id)
            elif req.role == "worker":
                q = q.eq("worker_id", req.user_id)
            else:
                q = None  # admin: don't fetch all orders
            if q:
                result = q.execute()
                if result.data:
                    user_orders = result.data if isinstance(result.data, list) else [result.data]
        except Exception:
            pass

    try:
        reply = await chat_with_agent(
            message=req.message,
            role=req.role,
            page=req.page,
            order_info=order_info,
            user_orders=user_orders,
            history=req.history,
        )
        return {"reply": reply}
    except Exception:
        return {"reply": MOCK_REPLY}
