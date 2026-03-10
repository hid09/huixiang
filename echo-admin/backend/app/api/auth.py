from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.admin import AdminLoginRequest, AdminUserBase, TokenResponse
from app.services.auth_service import AuthService
from app.dependencies import get_current_admin
from app.models import AdminUser

router = APIRouter(prefix="/api/admin", tags=["认证"])


@router.post("/login", summary="管理员登录")
async def login(
    request: AdminLoginRequest,
    db: Session = Depends(get_db),
):
    """管理员登录接口"""
    admin = AuthService.authenticate(db, request.username, request.password)
    if not admin:
        return ApiResponse[None](code=401, message="用户名或密码错误", data=None)

    token = AuthService.create_token(admin)
    user_data = AdminUserBase(id=admin.id, username=admin.username, role=admin.role)
    return ApiResponse[TokenResponse](code=200, message="登录成功", data=TokenResponse(token=token, user=user_data))


@router.post("/logout", summary="退出登录")
async def logout():
    """退出登录接口（前端删除 token 即可）"""
    return ApiResponse[None](code=200, message="退出成功", data=None)


@router.get("/me", summary="获取当前用户信息")
async def get_me(current_admin: AdminUser = Depends(get_current_admin)):
    """获取当前登录的管理员信息"""
    user_data = AdminUserBase(id=current_admin.id, username=current_admin.username, role=current_admin.role)
    return ApiResponse[AdminUserBase](code=200, data=user_data)
