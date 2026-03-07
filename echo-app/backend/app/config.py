"""
回响 - 配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 应用配置
APP_NAME = "回响"
APP_VERSION = "0.1.0"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./echo.db")

# AI服务配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")

# CORS配置
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://192.168.5.231:5173",
    "http://192.168.5.231:5174",
    "http://192.168.5.231:5175",
    "http://192.168.5.231:5176",
    "https://localhost:5173",
    "https://127.0.0.1:5173",
    "https://192.168.5.231:5173",
]

# JWT配置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "echo-jwt-secret-key-change-in-production-2024")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天过期
