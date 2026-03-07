"""
日记相关 API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.diary import DiaryGenerateRequest, DiaryResponse, DiaryListResponse
from app.services import diary_service
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/diaries", tags=["日记"])
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=ApiResponse[DiaryResponse])
async def generate_diary(
    request: DiaryGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成日记

    根据指定日期的记录，调用 AI 生成结构化日记
    """
    try:
        # 验证日期格式
        try:
            datetime.strptime(request.date, "%Y-%m-%d")
        except ValueError:
            return ApiResponse(
                success=False,
                data=None,
                message="日期格式错误，应为 YYYY-MM-DD"
            )

        diary = await diary_service.generate_diary(db, current_user.id, request.date)

        if not diary:
            return ApiResponse(
                success=False,
                data=None,
                message="当日无记录，无法生成日记"
            )

        return ApiResponse(
            data=diary,
            message="日记生成成功"
        )

    except Exception as e:
        logger.error(f"生成日记失败: {e}")
        return ApiResponse(
            success=False,
            data=None,
            message=f"生成失败: {str(e)}"
        )


@router.get("", response_model=ApiResponse[dict])
async def get_diary_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取日记列表"""
    result = diary_service.get_diary_list(db, current_user.id, page, page_size)
    return ApiResponse(data=result)


@router.get("/{date}", response_model=ApiResponse[DiaryResponse])
async def get_diary_by_date(
    date: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定日期的日记

    如果日记不存在但有记录，则自动生成
    """
    try:
        # 验证日期格式
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return ApiResponse(
                success=False,
                data=None,
                message="日期格式错误，应为 YYYY-MM-DD"
            )

        # 先尝试获取已有日记
        diary = diary_service.get_diary_by_date(db, current_user.id, date)

        if not diary:
            # 尝试生成
            diary = await diary_service.generate_diary(db, current_user.id, date)

            if not diary:
                return ApiResponse(
                    success=False,
                    data=None,
                    message="当日无记录"
                )

        return ApiResponse(data=diary)

    except Exception as e:
        logger.error(f"获取日记失败: {e}")
        return ApiResponse(
            success=False,
            data=None,
            message=f"获取失败: {str(e)}"
        )


@router.get("/stats/empty-days", response_model=ApiResponse[dict])
async def get_consecutive_empty_days(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取连续未记录天数（供首页渐进式关怀使用）

    返回从今天往前数，连续没有日记的天数
    """
    import time
    t_start = time.time()
    try:
        days = diary_service.get_consecutive_empty_days(db, current_user.id)
        t_end = time.time()
        print(f"📊 [/diaries/stats/empty-days] 耗时: {t_end-t_start:.3f}秒, 连续未记录: {days}天", flush=True)
        return ApiResponse(data={"consecutive_empty_days": days})
    except Exception as e:
        logger.error(f"获取连续未记录天数失败: {e}")
        return ApiResponse(
            success=False,
            data={"consecutive_empty_days": 0},
            message=f"获取失败: {str(e)}"
        )
