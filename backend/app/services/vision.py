import json
import httpx
from app.config import settings

CATEGORY_PROMPT = """你是一个校园维修助手。根据图片判断维修问题，并生成一条简洁的问题描述。

## 分类依据（按视觉线索判断）
- 电路/灯具：灯管、灯泡、开关、插座、电线、配电箱
- 供水/管道：水龙头、水管、阀门、水表、漏水痕迹
- 家具/门窗：桌椅、床铺、柜子、门框、窗户玻璃
- 空调/电器：空调内外机、风扇、热水器、电器面板
- 网络/弱电：网线、路由器、交换机、弱电箱
- 墙面/渗水：墙皮脱落、水渍、发霉、裂缝
- 锁具/五金：门锁、门把手、合页、五金件
- 卫生/下水：马桶、蹲坑、洗手池、地漏、下水管

## 难度判断
- simple: 单人15分钟内能解决（换灯管、拧螺丝、通下水）
- medium: 需要携带配件、30分钟以上（换水龙头、修门锁）
- complex: 需要大型工具或多人协作（墙面渗水、空调加氟、线路改造）

## 紧急度评分 urgency_score（0-100 整数）
- 90-100：涉及人身安全（漏电、漏气、爆水管、大面积积水触电风险）
- 70-89：大面积设施停用影响多人（整层断电、整栋停水、空调全坏）
- 40-69：影响正常使用但不紧急（单个灯不亮、水龙头滴水、门锁卡顿）
- 0-39：小问题可延后处理（墙面污渍、螺丝松动、外观瑕疵）
注意：即便问题本身不严重，如果描述中提到"急"、"马上"、"立刻"、"考试"、"上课"等关键词，也应适当提高 urgency_score。

## Few-shot 示例

示例1：
图片：一盏不亮的日光灯
输出：{"category":"电路/灯具","worker_type":"电工","description":"日光灯管不亮，疑似灯管烧坏或镇流器故障","suggested_parts":["日光灯管","镇流器"],"complexity":"simple","urgency":"normal","urgency_score":35,"confidence":0.9}

示例2：
图片：水龙头一直在滴水，下方有水渍
输出：{"category":"供水/管道","worker_type":"水工","description":"水龙头关不紧持续滴水","suggested_parts":["水龙头密封圈","水龙头阀芯"],"complexity":"medium","urgency":"normal","urgency_score":45,"confidence":0.85}

示例3：
图片：墙面大面积渗水发霉脱皮
输出：{"category":"墙面/渗水","worker_type":"泥水工","description":"墙面大面积渗水导致墙皮脱落发霉","suggested_parts":["防水涂料","腻子粉","墙面漆"],"complexity":"complex","urgency":"urgent","urgency_score":72,"confidence":0.9}

示例4：
图片：马桶堵塞，水溢出地面
输出：{"category":"卫生/下水","worker_type":"管道工","description":"马桶堵塞导致污水溢出","suggested_parts":["管道疏通剂","马桶搋子"],"complexity":"simple","urgency":"urgent","urgency_score":88,"confidence":0.88}

请严格按以下 JSON 格式返回，不要输出其他内容：
{
  "category": "电路/灯具|供水/管道|家具/门窗|空调/电器|网络/弱电|墙面/渗水|锁具/五金|卫生/下水|其它",
  "worker_type": "电工|水工|木工|空调师傅|弱电师傅|泥水工|锁匠|管道工|通用维修工",
  "description": "用一句话描述图中看到的具体问题，20字以内",
  "suggested_parts": ["配件1", "配件2"],
  "complexity": "simple|medium|complex",
  "urgency": "normal|urgent",
  "urgency_score": 0-100整数,
  "confidence": 0.0-1.0
}"""


async def analyze_image(image_url: str) -> dict:
    """用智谱 GLM-4.6V-Flash 分析维修图片"""
    if not settings.zhipu_api_key:
        return _mock_analysis()

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.zhipu_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "glm-4.6v-flash",
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
    return {
        "category": "其它",
        "worker_type": "通用维修工",
        "description": "疑似设备故障，需现场确认",
        "suggested_parts": [],
        "complexity": "simple",
        "urgency": "normal",
        "confidence": 0.0,
    }
