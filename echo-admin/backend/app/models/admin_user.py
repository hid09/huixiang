from sqlalchemy import Column, Integer, String, TIMESTAMP, Enum as SQLEnum
from sqlalchemy.sql import func

from app.database import Base


class AdminUser(Base):
    """管理员用户表（自有表，可写）"""

    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum("super", "viewer", name="admin_role"), default="viewer", nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username='{self.username}', role='{self.role}')>"
