import httpx
from app.config import settings

AMAP_GEOCODE_URL = "https://restapi.amap.com/v3/geocode/geo"
AMAP_DIRECTION_URL = "https://restapi.amap.com/v3/direction/driving"


async def geocode(address: str, city: str = "") -> dict | None:
    """高德地理编码：文本地址 → 经纬度"""
    if not settings.amap_api_key:
        return None
    params = {"key": settings.amap_api_key, "address": address}
    if city:
        params["city"] = city
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(AMAP_GEOCODE_URL, params=params)
        data = resp.json()
        if data.get("status") == "1" and data.get("geocodes"):
            geo = data["geocodes"][0]
            location = geo["location"]
            lng, lat = location.split(",")
            return {"lat": float(lat), "lng": float(lng), "formatted": geo.get("formatted_address", address)}
    return None


async def plan_route(origin: str, stops: list[dict]) -> dict | None:
    """高德驾车路径规划：起点 → 途经点 → 终点

    stops: [{"lng": 116.xx, "lat": 39.xx, "name": "工单名称"}, ...]
    返回最优路线，最多支持16个途经点
    """
    if not settings.amap_api_key or not stops:
        return None

    if len(stops) == 1:
        # 只有一个目的地，直接一对一路径
        dest = f"{stops[0]['lng']},{stops[0]['lat']}"
        params = {
            "key": settings.amap_api_key,
            "origin": origin,
            "destination": dest,
            "extensions": "base",
            "strategy": "0",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(AMAP_DIRECTION_URL, params=params)
            data = resp.json()
            if data.get("status") == "1" and data.get("route"):
                route = data["route"]["paths"][0]
                return _parse_route(route, stops)
        return None

    # 多途经点：使用 waypoints
    dest = f"{stops[-1]['lng']},{stops[-1]['lat']}"
    waypoints = []
    for s in stops[:-1]:
        waypoints.append(f"{s['lng']},{s['lat']}")

    params = {
        "key": settings.amap_api_key,
        "origin": origin,
        "destination": dest,
        "waypoints": ";".join(waypoints[:16]),  # 高德限制最多16个途经点
        "extensions": "base",
        "strategy": "0",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(AMAP_DIRECTION_URL, params=params)
        data = resp.json()
        if data.get("status") == "1" and data.get("route"):
            route = data["route"]["paths"][0]
            return _parse_route(route, stops)

    return None


def _parse_route(route: dict, stops: list) -> dict:
    """解析高德路线数据"""
    steps = []
    for step in route.get("steps", []):
        polyline = step.get("polyline", "")
        steps.append({
            "instruction": step.get("instruction", ""),
            "road": step.get("road", ""),
            "distance": int(step.get("distance", 0)),
            "polyline": polyline,
        })

    # 收集途经点坐标用于标记
    markers = []
    for i, s in enumerate(stops):
        markers.append({
            "name": s.get("name", f"工单{i+1}"),
            "order_id": s.get("order_id", ""),
            "lng": float(s["lng"]),
            "lat": float(s["lat"]),
            "index": i + 1,
        })

    return {
        "distance": int(route.get("distance", 0)),
        "duration": int(route.get("duration", 0)),
        "steps": steps,
        "markers": markers,
    }
