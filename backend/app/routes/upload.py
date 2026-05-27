import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.supabase import get_supabase
from app.services.vision import analyze_image

router = APIRouter()
MAX_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    if file.size and file.size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="图片不能超过 5MB")

    contents = await file.read()
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    file_name = f"{uuid.uuid4().hex}.{ext}"

    supabase = get_supabase()
    supabase.storage_upload("repair-images", file_name, contents, file.content_type or "image/jpeg")
    url = supabase.storage_public_url("repair-images", file_name)
    return {"url": url}


@router.post("/analyze")
async def analyze_repair_image(file: UploadFile = File(...)):
    if file.size and file.size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="图片不能超过 5MB")

    contents = await file.read()
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    file_name = f"{uuid.uuid4().hex}.{ext}"

    supabase = get_supabase()
    supabase.storage_upload("repair-images", file_name, contents, file.content_type or "image/jpeg")
    image_url = supabase.storage_public_url("repair-images", file_name)

    analysis = await analyze_image(image_url)
    return {"url": image_url, "analysis": analysis}
