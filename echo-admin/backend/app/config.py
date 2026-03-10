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

    # 数据库配置（支持 SQLite 和 MySQL）
    DATABASE_URL: str = "sqlite:////Users/jianguo/Desktop/test/echo-admin/backend/echo_admin.db"  # 使用绝对路径

    # MySQL 配置（可选，用于生产环境）
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "echo_readonly"
    DB_PASSWORD: str = ""
    DB_NAME: str = "echo_db"

    # CORS 配置
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def USE_SQLITE(self) -> bool:
        """判断是否使用 SQLite"""
        return self.DATABASE_URL.startswith("sqlite")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
