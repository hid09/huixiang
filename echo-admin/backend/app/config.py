from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "回响后台管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # 主数据库（存储管理员账号）
    DATABASE_URL: str = "sqlite:////app/data/echo_admin.db"

    # 回响数据库（只读，读取用户数据）
    ECHO_DATABASE_URL: str = "sqlite:////app/data/echo.db"

    # CORS 配置
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
