from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api import auth_router, users_router, dashboard_router, admin_users_router, diaries_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建表（仅自有表 admin_users）
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时的清理工作


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(dashboard_router)
app.include_router(admin_users_router)
app.include_router(diaries_router)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "回响后台管理系统 API", "version": settings.APP_VERSION}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}
