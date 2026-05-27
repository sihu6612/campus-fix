from fastapi import APIRouter, HTTPException
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
