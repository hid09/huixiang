"""
回响 - FastAPI 主入口

Slogan: 回响，陪你听见自己
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, APP_VERSION, CORS_ORIGINS, DEBUG
from app.database import init_db
from app.api import users_router, records_router, diaries_router, reviews_router
from app.scheduler import start_scheduler, shutdown_scheduler

# 创建FastAPI应用
app = FastAPI(
    title=APP_NAME,
    description="语音成长日记 - 语音输入 + AI智能分析的个人成长记录工具",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users_router)
app.include_router(records_router)
app.include_router(diaries_router)
app.include_router(reviews_router)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print(f"🚀 {APP_NAME} 启动中...")
    init_db()
    # 启动定时任务调度器
    start_scheduler()
    print(f"✅ {APP_NAME} v{APP_VERSION} 启动成功！")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    shutdown_scheduler()
    print(f"👋 {APP_NAME} 已关闭")


@app.get("/")
async def root():
    """根路径 - 健康检查"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "message": "回响，陪你听见自己"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
