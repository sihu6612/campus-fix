from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth, orders, messages, upload

app = FastAPI(title="校修通 CampusFix API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
