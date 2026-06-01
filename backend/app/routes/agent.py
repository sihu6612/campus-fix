from fastapi import APIRouter
from app.models.schemas import AgentChatRequest, AgentChatResponse
from app.services.agent import chat_with_agent, MOCK_REPLY
from app.services.supabase import get_supabase

router = APIRouter()


def _search_knowledge(message: str, limit: int = 3) -> list:
    """搜索知识库中与问题相关的已完工案例"""
    supabase = get_supabase()
    try:
        result = supabase.select(
            "repair_orders",
            "id,category,description,solution,suggested_parts,worker_id,created_at"
        ).eq("status", "completed").order("created_at", asc=False).limit(50).execute()

        orders = result.data or []
        # 关键词匹配
        keywords = set(message.lower().split())
        scored = []
        for o in orders:
            text = (o.get("description", "") + o.get("solution", "")).lower()
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scored.append((score, o))
        scored.sort(key=lambda x: x[0], reverse=True)

        # 填充师傅名
        worker_ids = {o["worker_id"] for _, o in scored[:limit] if o.get("worker_id")}
        profiles = {}
        if worker_ids:
            try:
                res = supabase.select("profiles", "id,display_name").in_("id", list(worker_ids)).execute()
                for p in (res.data or []):
                    profiles[p["id"]] = p["display_name"]
            except Exception:
                pass

        cases = []
        for _, o in scored[:limit]:
            cases.append({
                "category": o.get("category", ""),
                "description": o.get("description", "")[:80],
                "solution": o.get("solution", ""),
                "parts": o.get("suggested_parts") or [],
                "worker": profiles.get(o.get("worker_id"), ""),
            })
        return cases
    except Exception:
        return []


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
                q = None
            if q:
                result = q.execute()
                if result.data:
                    user_orders = result.data if isinstance(result.data, list) else [result.data]
        except Exception:
            pass

    # 搜索知识库
    knowledge_cases = None
    if req.message:
        knowledge_cases = _search_knowledge(req.message)

    try:
        reply = await chat_with_agent(
            message=req.message,
            role=req.role,
            page=req.page,
            order_info=order_info,
            user_orders=user_orders,
            history=req.history,
            knowledge_cases=knowledge_cases,
        )
        return {"reply": reply}
    except Exception:
        return {"reply": MOCK_REPLY}
