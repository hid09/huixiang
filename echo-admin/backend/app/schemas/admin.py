from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    """管理员登录请求"""

    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class AdminUserBase(BaseModel):
    """管理员用户基础信息"""

    id: int
    username: str
    role: str


class AdminUserResponse(AdminUserBase):
    """管理员用户响应"""

    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """登录成功响应"""

    token: str
    user: AdminUserBase


class AdminUserCreate(BaseModel):
    """创建管理员请求"""

    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码，至少6位")
    role: str = Field("viewer", description="角色：super 或 viewer")


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""

    new_password: str = Field(..., min_length=6, description="新密码，至少6位")
