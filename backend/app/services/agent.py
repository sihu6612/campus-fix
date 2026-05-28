import httpx
from app.config import settings

SYSTEM_PROMPT = """你是校园维修平台「校修通 CampusFix」的智能客服助手。你的职责是帮助用户了解平台功能、解答报修流程问题、解释工单状态含义。

平台有三种角色：
- 学生 (student)：提交报修工单，跟踪维修进度，确认完工
- 师傅 (worker)：接单、维修、提交完工
- 管理员 (admin)：分配工单给师傅，管理整体维修工作

工单状态流转：
  pending(待分配) → assigned(已分配) → in_progress(维修中) → awaiting_confirmation(待确认) → completed(已完成)
  任意阶段可 → cancelled(已取消)

回答要求：
- 用中文、友好热情的语气回答
- 如果用户询问维修进度，引导他们查看工单详情页的进度时间线
- 如果用户报告新问题，引导他们去「报修」页面提交工单
- 如果用户是师傅且询问如何操作，讲解接单和完工流程
- 如果用户是管理员且询问如何分配，讲解分配师傅的操作
- 回答简洁，不超过200字"""

MOCK_REPLY = "你好！我是校修通智能助手（当前为离线模式）。请参考页面上的帮助信息，或联系管理员获取支持。"


async def chat_with_agent(message: str, role: str, page: str, order_info: dict | None = None) -> str:
    if not settings.deepseek_api_key:
        return MOCK_REPLY

    role_names = {"student": "学生", "worker": "师傅", "admin": "管理员"}
    context = f"当前用户角色：{role_names.get(role, role)}\n当前页面：{page}\n"
    if order_info:
        context += (
            f"正在查看工单：{order_info.get('category', '')} — "
            f"{order_info.get('location', '')}，"
            f"状态：{order_info.get('status', '')}，"
            f"描述：{order_info.get('description', '')}"
        )
    else:
        context += "(未在查看具体工单)"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context},
        {"role": "user", "content": message},
    ]

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "max_tokens": 500,
                },
            )
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return content.strip().removeprefix("```").removesuffix("```").strip()
    except Exception:
        return MOCK_REPLY
