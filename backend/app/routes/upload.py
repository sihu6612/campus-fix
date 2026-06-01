import uuid
import base64
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.supabase import get_supabase
from app.services.vision import analyze_image

router = APIRouter()
MAX_SIZE = 5 * 1024 * 1024  # 5MB


class AnalyzeRequest(BaseModel):
    image_base64: str  # data:image/jpeg;base64,xxx 或纯 base64


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


def _decode_and_upload(b64_data: str) -> tuple[str, str, bytes]:
    """解析 base64 图片，上传到 Supabase，返回 (公网URL, 文件名, 原始字节)"""
    if b64_data.startswith("data:"):
        # data:image/jpeg;base64,xxx
        header, b64_data = b64_data.split(",", 1)
        mime = header.split(":")[1].split(";")[0]
        ext = mime.split("/")[-1] if "/" in mime else "jpg"
    else:
        mime = "image/jpeg"
        ext = "jpg"

    try:
        contents = base64.b64decode(b64_data)
    except Exception:
        raise HTTPException(status_code=400, detail="无效的 base64 图片数据")

    file_name = f"{uuid.uuid4().hex}.{ext}"
    supabase = get_supabase()
    supabase.storage_upload("repair-images", file_name, contents, mime)
    image_url = supabase.storage_public_url("repair-images", file_name)
    return image_url, file_name, contents


@router.post("/analyze/fast")
async def analyze_fast(req: AnalyzeRequest):
    """快速分析：前端 base64 直传，跳过 Supabase 上传等待"""
    # 先调 AI 分析（用 base64 data URL，不等 Supabase）
    analysis = await analyze_image(req.image_base64)

    # 异步保存图片（失败不影响分析结果）
    try:
        image_url, _, _ = _decode_and_upload(req.image_base64)
    except Exception:
        image_url = ""

    return {"url": image_url, "analysis": analysis}


@router.post("/analyze")
async def analyze_repair_image(file: UploadFile = File(...)):
    """传统方式：FormData 上传"""
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
