"""师傅匹配评分算法"""

# 技能到 worker_type 的映射
SKILL_TO_TYPE = {
    "电路/灯具": "电工",
    "供水/管道": "水工",
    "家具/门窗": "木工",
    "空调/电器": "空调师傅",
    "网络/弱电": "弱电师傅",
    "墙面/渗水": "泥水工",
    "锁具/五金": "锁匠",
    "卫生/下水": "管道工",
}


def score_worker(worker: dict, order: dict) -> dict:
    """对单个师傅打分，返回分数明细"""
    score = 0
    reasons = []

    # 1. 技能匹配 (0-30分)
    order_category = order.get("category", "")
    expected_type = SKILL_TO_TYPE.get(order_category, "")
    skills = worker.get("skills") or []
    worker_type = worker.get("worker_type", "")

    if isinstance(skills, str):
        import json
        try:
            skills = json.loads(skills)
        except (json.JSONDecodeError, TypeError):
            skills = [s.strip() for s in skills.split(",") if s.strip()]

    # 精确 worker_type 匹配
    if expected_type and worker_type == expected_type:
        score += 20
        reasons.append(f"技能类型匹配 (+20)")
    elif expected_type and expected_type in skills:
        score += 25
        reasons.append(f"技能标签匹配 (+25)")
    elif worker_type == "通用维修工":
        score += 10
        reasons.append("通用维修工 (+10)")
    else:
        # 部分匹配：检查 skills 中的标签是否包含关键词
        partial = False
        for sk in (skills or []):
            if sk and (sk in order_category or any(w in sk for w in order_category.split("/"))):
                score += 15
                reasons.append(f"技能部分匹配 (+15)")
                partial = True
                break
        if not partial:
            reasons.append("技能不匹配 (+0)")

    # 2. 负载惩罚 (0-15分)
    current_load = worker.get("current_load", 0) or 0
    load_penalty = min(current_load * 5, 15)
    score += (15 - load_penalty)
    reasons.append(f"负载 {current_load}单 (-{load_penalty})")

    # 3. 位置接近 (0-10分)
    w_lat, w_lng = worker.get("lat"), worker.get("lng")
    o_lat, o_lng = order.get("lat"), order.get("lng")
    if w_lat and w_lng and o_lat and o_lng:
        dist = _haversine(w_lat, w_lng, o_lat, o_lng)
        if dist < 0.5:
            score += 10
            reasons.append(f"位置很近 (+10)")
        elif dist < 2:
            score += 7
            reasons.append(f"位置较近 (+7)")
        elif dist < 5:
            score += 3
            reasons.append(f"位置一般 (+3)")
        else:
            reasons.append(f"距离较远 {dist:.1f}km")
    else:
        reasons.append("无位置数据")

    # 4. 紧急度加成 (0-5分)
    urgency_score_val = order.get("urgency_score", 0) or 0
    if urgency_score_val >= 80 and score >= 20:
        score += 5
        reasons.append("紧急工单加成 (+5)")
    elif urgency_score_val >= 40:
        score += 2
        reasons.append("中等紧急加成 (+2)")

    return {
        "worker_id": worker.get("id"),
        "worker_name": worker.get("display_name", ""),
        "worker_type": worker_type,
        "skills": skills,
        "current_load": current_load,
        "score": score,
        "max_score": 50,
        "reasons": reasons,
    }


def suggest_workers(workers: list, order: dict) -> list:
    """对所有师傅打分排序，返回推荐列表"""
    scored = [score_worker(w, order) for w in workers]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def _haversine(lat1, lng1, lat2, lng2):
    """计算两点距离（公里）"""
    from math import radians, cos, sin, asin, sqrt
    r = 6371
    lat1, lng1, lat2, lng2 = map(radians, [float(lat1), float(lng1), float(lat2), float(lng2)])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 2 * r * asin(sqrt(a))
