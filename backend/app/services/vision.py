import json
import httpx
from app.config import settings

CATEGORY_PROMPT = """你是一个校园维修助手。根据图片判断维修问题的大类。

请严格按以下 JSON 格式返回，不要输出其他内容：
{
  "category": "电路/灯具|供水/管道|家具/门窗|空调/电器|网络/弱电|墙面/渗水|锁具/五金|卫生/下水|其它",
  "worker_type": "电工|水工|木工|空调师傅|弱电师傅|泥水工|锁匠|管道工|通用维修工",
  "suggested_parts": ["配件1", "配件2"],
  "complexity": "simple|medium|complex",
  "urgency": "normal|urgent",
  "confidence": 0.0-1.0
}

判断标准：
- simple: 单人15分钟内能解决（换灯管、拧螺丝、通下水）
- medium: 需要携带配件、30分钟以上（换水龙头、修门锁）
- complex: 需要大型工具或多人协作（墙面渗水、空调加氟、线路改造）
- urgent: 影响安全或大面积停用（漏电、爆水管、整层断电）"""


async def analyze_image(image_url: str) -> dict:
    """用通义千问 VL 分析维修图片"""
    if not settings.dashscope_api_key:
        return _mock_analysis()

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.dashscope_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "qwen-vl-plus",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_url}},
                            {"type": "text", "text": CATEGORY_PROMPT},
                        ],
                    }
                ],
                "max_tokens": 300,
            },
        )
        data = resp.json()
        try:
            content = data["choices"][0]["message"]["content"]
            content = content.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(content)
        except (KeyError, json.JSONDecodeError):
            return _mock_analysis()


def _mock_analysis() -> dict:
    """当没有 AI API key 时返回空结果"""
    return {
        "category": "其它",
        "worker_type": "通用维修工",
        "suggested_parts": [],
        "complexity": "simple",
        "urgency": "normal",
        "confidence": 0.0,
    }
