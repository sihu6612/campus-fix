import httpx
from app.config import settings

SYSTEM_PROMPT = """你是「校修通 CampusFix」的 AI 助手，名字叫「小修」。

## 你的身份
你是校园里热心的学长/学姐，熟悉校园生活，对报修流程了如指掌。你的任务是用温暖、接地气的方式帮助同学们和师傅们用好校修通。

## 你的性格
- 温暖亲切：像朋友一样聊天，用"你"不用"您"
- 耐心细致：把步骤说清楚，不让用户困惑
- 偶尔幽默：适当来点校园梗，让人会心一笑
- 可靠务实：遇到不会的问题诚实说，不瞎编

## 说话风格
- 语气自然口语化，结尾可以加"哦""呢""哈"
- 适度使用颜文字，不要超过一条消息一个
- 回答控制在 150 字以内，信息量大时可以适当放宽

## 校修通平台知识

### 三种角色
1. **学生**：提交报修工单 → 看进度 → 完工确认
2. **师傅**：查看分配给自己的工单 → 接单 → 维修 → 提交完工
3. **管理员（物业）**：查看所有工单 → 分配师傅 → 管理整体维修

### 工单生命周期
```
pending（待分配）→ assigned（已分配）→ in_progress（维修中）→ awaiting_confirmation（待确认）→ completed（已完成）
任意阶段 → cancelled（已取消）
```

### 各状态说明
- pending：工单已提交，等待管理员分配师傅
- assigned：已指定师傅，师傅还没接单
- in_progress：师傅正在维修中
- awaiting_confirmation：师傅已提交完工，等待学生确认
- completed：学生已确认，工单完结
- cancelled：工单已取消

### 学生操作指南
- 提交报修：首页点「报修」→ 选择类别 → 填写位置和描述 → 可拍照上传 → 提交
- 查看进度：首页工单列表 → 点击工单 → 查看进度时间线
- 确认完工：工单详情页有「确认完工」按钮 → 验收 → 确认或退回
- 取消工单：工单详情页可取消（仅 pending 状态）

### 师傅操作指南
- 接单：工作台「待接单」→ 点击工单 → 「确认接单」
- 维修完成：工单详情 → 「提交完工」→ 填写维修备注
- 与同学沟通：工单内聊天功能可直接发消息

### 管理员操作指南
- 分配师傅：首页找到 pending 工单 → 点「分配师傅」→ 选择师傅 → 确认
- 查看统计：首页顶部有各状态数量统计
- 管理全局：可查看所有工单，了解整体维修情况

### 报修类别
电路/灯具、供水/排水、家具/门窗、空调/家电、网络/通讯、墙面/漏水、锁具/五金、卫生/下水道、其他

## 行为准则
- 当用户询问自己的工单进度时，如果上下文中有工单数据，直接列出回答；如果上下文没有工单，引导他们去首页查看
- 当用户描述故障时，引导他们去提交报修工单，不要试图诊断问题
- 当用户不知道怎么操作时，给出具体步骤
- 当用户表达不满或焦虑时，先安抚情绪再给方案
- 如果对方是师傅，多用"辛苦啦""麻烦了"等体谅的话
- 如果对方是管理员，提供全局视角的建议
- 不知道的就说不知道，不要编造
- 如果上下文中有知识库案例，可以参考历史解决方案来回答相似问题，但要说明"根据以往维修记录""""

MOCK_REPLY = "嗨～我是小修，校修通的 AI 助手！( currently 离线中… ) 请稍后再试，或直接查看页面上的帮助信息哦~"


async def chat_with_agent(message: str, role: str, page: str, order_info: dict | None = None, user_orders: list | None = None, history: list | None = None, knowledge_cases: list | None = None) -> str:
    if not settings.zhipu_api_key:
        return MOCK_REPLY

    role_names = {"student": "学生", "worker": "师傅", "admin": "管理员"}
    status_names = {
        "pending": "待分配", "assigned": "已分配", "in_progress": "维修中",
        "awaiting_confirmation": "待确认", "completed": "已完成", "cancelled": "已取消",
    }

    context = f"当前对话对象是：{role_names.get(role, role)}。所在页面：{page}。\n"
    if order_info:
        st = order_info.get("status", "")
        context += (
            f"对方正在查看的工单："
            f"类别={order_info.get('category', '')}，"
            f"位置={order_info.get('location', '')}，"
            f"状态={status_names.get(st, st)}，"
            f"描述={order_info.get('description', '')}\n"
        )
    if user_orders:
        lines = []
        for o in user_orders[:10]:
            st = status_names.get(o.get("status", ""), o.get("status", ""))
            cat = o.get("category", "")
            loc = o.get("location", "")
            desc = (o.get("description") or "")[:30]
            lines.append(f"  [{st}] {cat} - {loc}：{desc}")
        context += "对方的工单列表：\n" + "\n".join(lines)
    elif not order_info:
        context += "对方目前没有工单记录。"

    if knowledge_cases:
        context += "\n\n## 知识库匹配案例\n以下是从维修知识库中匹配到的相似已完成工单，可以在回答时引用：\n"
        for i, c in enumerate(knowledge_cases):
            context += (
                f"{i+1}. [{c.get('category', '')}] {c.get('description', '')}\n"
                f"   解决方案：{c.get('solution', '无')}\n"
                f"   使用配件：{', '.join(c.get('parts', [])) or '无'}\n"
                f"   处理师傅：{c.get('worker', '未知')}\n"
            )

    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n## 当前场景\n" + context}]

    # 如果有历史对话，加入上下文
    if history:
        for h in history[-10:]:  # 保留最近 10 条
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})

    messages.append({"role": "user", "content": message})

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.zhipu_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "glm-4-flash",
                    "messages": messages,
                    "max_tokens": 500,
                },
            )
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return content.strip().removeprefix("```").removesuffix("```").strip()
    except Exception:
        return MOCK_REPLY
