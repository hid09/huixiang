from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# 主数据库引擎（存储管理员账号）
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

# 回响数据库引擎（只读，读取用户数据）
echo_engine = create_engine(
    settings.ECHO_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
EchoSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=echo_engine)

# 创建基类
Base = declarative_base()


def get_db():
    """获取主数据库会话（管理员账号）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_echo_db():
    """获取回响数据库会话（用户数据，只读）"""
    db = EchoSessionLocal()
    try:
        yield db
    finally:
        db.close()
