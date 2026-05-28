from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# --- 用户 ---
class UserRegister(BaseModel):
    email: str
    password: str
    display_name: str
    role: str = "student"  # student / worker / admin


class UserLogin(BaseModel):
    email: str
    password: str


class UserProfile(BaseModel):
    id: UUID
    role: str
    display_name: str
    phone: str = ""
    avatar_url: str = ""
    worker_type: Optional[str] = None


# --- 工单 ---
class OrderCreate(BaseModel):
    category: str = ""
    location: str = ""
    description: str = ""
    image_urls: List[str] = []
    urgency: str = "normal"
    ai_analysis: Optional[dict] = None
    suggested_parts: List[str] = []
    complexity: str = "simple"


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    worker_id: Optional[UUID] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    complexity: Optional[str] = None


class OrderResponse(BaseModel):
    id: UUID
    student_id: UUID
    worker_id: Optional[UUID] = None
    category: str
    location: str
    description: str
    image_urls: List[str]
    ai_analysis: Optional[dict] = None
    suggested_parts: List[str]
    complexity: str
    status: str
    urgency: str
    rating: Optional[int] = None
    review: str = ""
    created_at: datetime
    updated_at: datetime
    # joined
    student_name: str = ""
    worker_name: str = ""


# --- 消息 ---
class MessageCreate(BaseModel):
    order_id: UUID
    content: str
    image_url: Optional[str] = None


class MessageResponse(BaseModel):
    id: UUID
    order_id: UUID
    sender_id: UUID
    content: str
    image_url: Optional[str] = None
    created_at: datetime
    sender_name: str = ""


# --- 状态日志 ---
class StatusLogResponse(BaseModel):
    id: UUID
    order_id: UUID
    from_status: Optional[str]
    to_status: str
    operator_id: UUID
    note: str
    created_at: datetime
    operator_name: str = ""


# --- AI 图片分析 ---
class ImageAnalysisResult(BaseModel):
    category: str = ""
    worker_type: str = ""
    suggested_parts: List[str] = []
    complexity: str = "simple"
    urgency: str = "normal"
    confidence: float = 0.0


# --- AI 智能客服 ---
class AgentChatRequest(BaseModel):
    message: str
    role: str = "student"
    page: str = ""
    order_id: Optional[str] = None


class AgentChatResponse(BaseModel):
    reply: str
