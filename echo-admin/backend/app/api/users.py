from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_echo_db
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.user import UserResponse, UserDetailResponse, RecordResponse, DiaryResponse
from app.services.user_service import UserService
from app.dependencies import get_current_admin
from app.models import AdminUser

router = APIRouter(prefix="/api/admin/users", tags=["用户管理"])


@router.get("", summary="获取用户列表")
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词（用户名/手机号）"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db: Session = Depends(get_echo_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """获取用户列表（支持分页和搜索）"""
    total, items = UserService.get_users(db, page, page_size, keyword, start_date, end_date)
    return ApiResponse(
        code=200,
        data={"total": total, "items": items},
    )


@router.get("/{user_id}", summary="获取用户详情")
async def get_user_detail(
    user_id: str,  # UUID 字符串
    db: Session = Depends(get_echo_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """获取用户详情"""
    user = UserService.get_user_detail(db, user_id)
    if not user:
        return ApiResponse(code=404, message="用户不存在", data=None)
    return ApiResponse(code=200, data=user)


@router.get("/{user_id}/records", summary="获取用户录音记录")
async def get_user_records(
    user_id: str,  # UUID 字符串
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_echo_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """获取用户录音记录"""
    total, items = UserService.get_user_records(db, user_id, page, page_size)
    return ApiResponse(
        code=200,
        data={"total": total, "items": items},
    )


@router.get("/{user_id}/diaries", summary="获取用户日记记录")
async def get_user_diaries(
    user_id: str,  # UUID 字符串
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_echo_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """获取用户日记记录"""
    total, items = UserService.get_user_diaries(db, user_id, page, page_size)
    return ApiResponse(
        code=200,
        data={"total": total, "items": items},
    )
