"""
周回顾 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services import review_service

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/weekly")
async def get_weekly_review(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取本周周回顾（实时生成）

    数据来源：汇总日记表（daily_diaries）

    返回：
    - record_days: 本周记录天数
    - voice_count: 本周语音条数
    - dominant_emotion: 主导情绪 emoji
    - dominant_emotion_name: 主导情绪名称
    - emotion_trend: 情绪走势（周一到周日）
    - positive_ratio: 积极情绪占比
    - keywords: 关键词云
    - suggestions: AI 建议
    """
    try:
        user_id = current_user.id
        result = await review_service.get_weekly_review(db, user_id)
        return {"success": True, "data": result, "message": "周回顾生成成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成周回顾失败: {str(e)}")
