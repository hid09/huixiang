from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.admin import AdminUserResponse, AdminUserCreate, ResetPasswordRequest
from app.utils.password import get_password_hash
from app.dependencies import get_current_admin, require_super_admin
from app.models import AdminUser

router = APIRouter(prefix="/api/admin/admin-users", tags=["管理员管理"])


@router.get("", summary="获取管理员列表")
async def get_admin_users(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_super_admin),
):
    """获取管理员列表（仅超级管理员）"""
    admins = db.query(AdminUser).order_by(AdminUser.id).all()
    return ApiResponse[List[AdminUserResponse]](
        code=200,
        data=admins,
    )


@router.post("", summary="添加管理员")
async def create_admin_user(
    request: AdminUserCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_super_admin),
):
    """添加管理员（仅超级管理员）"""
    # 检查用户名是否已存在
    existing = db.query(AdminUser).filter(AdminUser.username == request.username).first()
    if existing:
        return ApiResponse[None](code=400, message="用户名已存在", data=None)

    # 创建管理员
    admin = AdminUser(
        username=request.username,
        password_hash=get_password_hash(request.password),
        role=request.role,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    return ApiResponse[AdminUserResponse](
        code=200,
        message="添加成功",
        data={
            "id": admin.id,
            "username": admin.username,
            "role": admin.role,
            "created_at": admin.created_at,
        },
    )


@router.post("/{admin_id}/reset-password", summary="重置密码")
async def reset_password(
    admin_id: int,
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(require_super_admin),
):
    """重置管理员密码（仅超级管理员）"""
    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if not admin:
        return ApiResponse[None](code=404, message="管理员不存在", data=None)

    admin.password_hash = get_password_hash(request.new_password)
    db.commit()

    return ApiResponse[None](code=200, message="密码重置成功", data=None)
