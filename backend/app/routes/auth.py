from fastapi import APIRouter, HTTPException, Query
from app.services.supabase import get_supabase
from app.models.schemas import UserRegister, UserLogin

router = APIRouter()


@router.post("/register")
def register(data: UserRegister):
    supabase = get_supabase()
    try:
        resp = supabase.auth_signup(data.email, data.password, {
            "display_name": data.display_name,
            "role": data.role,
            "class_name": data.class_name,
        })
        return {"user": resp.get("user"), "session": resp.get("session")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(data: UserLogin):
    supabase = get_supabase()
    try:
        resp = supabase.auth_login(data.email, data.password)
        return {"user": resp.get("user"), "session": resp.get("session")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/account")
def delete_account(user_id: str, access_token: str):
    """删除账号（需提供 user_id 和 access_token 验证身份）"""
    supabase = get_supabase()
    try:
        supabase.auth_delete_user(user_id, access_token)
        return {"ok": True, "message": "账号已删除"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/admin/register")
def admin_register(data: UserRegister, secret: str = ""):
    """隐藏的管理员注册入口，需要密钥"""
    if secret != "xiaoling2026":
        raise HTTPException(status_code=403, detail="无权访问")
    supabase = get_supabase()
    try:
        resp = supabase.auth_signup(data.email, data.password, {
            "display_name": data.display_name,
            "role": "admin",
            "class_name": "",
        })
        return {"user": resp.get("user"), "session": resp.get("session")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/users")
def list_users(admin_id: str = ""):
    """管理员获取所有用户列表"""
    supabase = get_supabase()
    try:
        # 验证是否为管理员
        profile = supabase.select("profiles", "role").eq("id", admin_id).single().execute()
        if not profile.data or profile.data.get("role") != "admin":
            raise HTTPException(status_code=403, detail="无权访问")
        result = supabase.select("profiles", "id,display_name,role,class_name,phone,created_at").order("created_at", asc=False).limit(200).execute()
        return result.data or []
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/users/{user_id}")
def admin_delete_user(user_id: str, admin_id: str = ""):
    """管理员删除任意用户"""
    supabase = get_supabase()
    try:
        profile = supabase.select("profiles", "role").eq("id", admin_id).single().execute()
        if not profile.data or profile.data.get("role") != "admin":
            raise HTTPException(status_code=403, detail="无权访问")
        supabase.auth_delete_user_admin(user_id)
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
