"""
用户模型
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # 认证字段
    username = Column(String(50), unique=True, index=True, nullable=True, comment="用户名")
    password_hash = Column(String(255), nullable=True, comment="密码哈希")
    device_id = Column(String, unique=True, index=True, nullable=True, comment="设备标识(兼容老用户)")

    # 基本信息
    name = Column(String(50), default="回响用户", comment="昵称")
    avatar = Column(String(255), nullable=True, comment="头像URL")
    timezone = Column(String(50), default="Asia/Shanghai", comment="时区")
    diary_time = Column(String(5), default="22:30", comment="日记生成时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 统计字段
    total_record_days = Column(Integer, default=0, comment="总记录天数")
    total_voice_count = Column(Integer, default=0, comment="总语音条数")
    continuous_days = Column(Integer, default=0, comment="连续记录天数")
    longest_continuous_days = Column(Integer, default=0, comment="最长连续天数")
    last_record_date = Column(String(10), nullable=True, comment="最后记录日期 YYYY-MM-DD")

    def __repr__(self):
        return f"<User {self.name}>"
