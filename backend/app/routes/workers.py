from fastapi import APIRouter, HTTPException, Query
from app.services.supabase import get_supabase
from app.services.worker_matching import suggest_workers
from app.services.geocode import geocode, plan_route
from typing import Optional

router = APIRouter()


@router.get("/")
def list_workers():
    supabase = get_supabase()
    result = supabase.select(
        "profiles",
        "id,display_name,worker_type,skills,current_load,lat,lng,is_available"
    ).eq("role", "worker").execute()
    return result.data or []


@router.post("/suggest")
def suggest(order_id: str = Query(...)):
    supabase = get_supabase()
    order_result = supabase.select("repair_orders", "*").eq("id", order_id).single().execute()
    if not order_result.data:
        raise HTTPException(status_code=404, detail="工单不存在")
    workers = list_workers()
    if not workers:
        return {"suggestions": [], "best": None}
    scored = suggest_workers(workers, order_result.data)
    return {"suggestions": scored, "best": scored[0] if scored else None}


@router.get("/{worker_id}/route")
async def get_worker_route(worker_id: str):
    supabase = get_supabase()

    # 获取师傅坐标
    worker = supabase.select("profiles", "id,display_name,lat,lng").eq("id", worker_id).single().execute()
    if not worker.data or not worker.data.get("lat"):
        raise HTTPException(status_code=400, detail="师傅未设置位置坐标")

    w = worker.data
    origin = f"{w['lng']},{w['lat']}"

    # 获取师傅进行中的工单（有坐标的）
    orders = supabase.select(
        "repair_orders", "id,category,location,lat,lng"
    ).eq("worker_id", worker_id).in_("status", ["assigned", "in_progress", "awaiting_confirmation"]).execute()

    stops = []
    for o in (orders.data or []):
        if o.get("lat") and o.get("lng"):
            stops.append({
                "order_id": o["id"],
                "name": f"{o['category']} - {o['location']}",
                "lat": o["lat"],
                "lng": o["lng"],
            })

    if not stops:
        return {"route": None, "message": "没有有坐标的进行中工单"}

    route = await plan_route(origin, stops)
    return {
        "route": route,
        "worker_name": w.get("display_name", ""),
        "origin": {"lng": w["lng"], "lat": w["lat"]},
        "stops_count": len(stops),
    }
