import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.routes import auth, orders, messages, upload

app = FastAPI(title="校修通 CampusFix", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


# 托管前端静态文件
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/campus-fix/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/campus-fix/{full_path:path}")
    async def serve_spa(full_path: str = ""):
        file_path = os.path.join(frontend_dist, full_path) if full_path else os.path.join(frontend_dist, "index.html")
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/campus-fix")
    async def serve_spa_root():
        return FileResponse(os.path.join(frontend_dist, "index.html"))
