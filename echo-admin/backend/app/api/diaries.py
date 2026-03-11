from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_echo_db
from app.schemas.common import ApiResponse
from app.schemas.user import DiaryDetailResponse
from app.services.user_service import UserService
from app.dependencies import get_current_admin
from app.models import AdminUser

router = APIRouter(prefix="/api/admin/diaries", tags=["日记管理"])


@router.get("/{diary_id}", summary="获取日记详情")
async def get_diary_detail(
    diary_id: str,  # UUID 字符串
    db: Session = Depends(get_echo_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """获取日记详情（含关联用户信息和录音记录）"""
    diary = UserService.get_diary_detail(db, diary_id)
    if not diary:
        return ApiResponse[None](code=404, message="日记不存在", data=None)
    return ApiResponse[DiaryDetailResponse](code=200, data=diary)
