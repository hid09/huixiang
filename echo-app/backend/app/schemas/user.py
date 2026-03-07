"""
用户相关Schema
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    """创建用户请求（老版本兼容）"""
    device_id: str
    name: Optional[str] = "回响用户"


class UserRegister(BaseModel):
    """注册请求"""
    username: str
    password: str
    name: Optional[str] = "回响用户"


class UserLogin(BaseModel):
    """登录请求"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: Optional[str] = None
    device_id: Optional[str] = None
    name: str
    avatar: Optional[str] = None
    timezone: str = "Asia/Shanghai"
    diary_time: str = "22:30"
    total_record_days: int = 0
    total_voice_count: int = 0
    continuous_days: int = 0
    longest_continuous_days: int = 0
    last_record_date: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_record_days: int
    total_voice_count: int
    continuous_days: int
    longest_continuous_days: int
    this_month_days: int
    this_month_percentage: float


class UserUpdate(BaseModel):
    """更新用户请求"""
    name: Optional[str] = None
    avatar: Optional[str] = None
    diary_time: Optional[str] = None
