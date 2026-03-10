from datetime import datetime, timedelta, date
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ApiResponse
from app.dependencies import get_current_admin
from app.models import AdminUser, User, Record, Diary

router = APIRouter(prefix="/api/admin/dashboard", tags=["数据看板"])


@router.get("/stats", summary="获取看板统计数据")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin),
):
    """获取看板统计数据：概览、AI健康度、7天趋势"""

    # 今日日期（用于 local_date 查询）
    today = date.today().strftime("%Y-%m-%d")

    # 1. 概览数据
    total_users = db.query(func.count(User.id)).scalar() or 0

    # DAU: 今日有录音记录的不重复用户数
    dau_today = (
        db.query(func.count(func.distinct(Record.user_id)))
        .filter(Record.local_date == today)
        .scalar() or 0
    )

    records_today = (
        db.query(func.count(Record.id))
        .filter(Record.local_date == today)
        .scalar() or 0
    )

    diaries_today = (
        db.query(func.count(Diary.id))
        .filter(Diary.diary_date == today)
        .scalar() or 0
    )

    overview = {
        "total_users": total_users,
        "dau_today": dau_today,
        "records_today": records_today,
        "diaries_today": diaries_today,
    }

    # 2. AI 健康度（基于日记数据）
    # 假设 thoughts_summary 为空表示生成失败
    success_count = (
        db.query(func.count(Diary.id))
        .filter(Diary.thoughts_summary.isnot(None), Diary.thoughts_summary != "[]")
        .scalar() or 0
    )
    total_diaries = db.query(func.count(Diary.id)).scalar() or 0
    fail_count = total_diaries - success_count
    fail_rate = (fail_count / total_diaries * 100) if total_diaries > 0 else 0

    ai_health = {
        "success_count": success_count,
        "fail_count": fail_count,
        "fail_rate": round(fail_rate, 1),
    }

    # 3. 7 天趋势
    trend_dates = []
    new_users = []
    active_users = []
    records = []
    diaries = []

    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        display_date = d.strftime("%m-%d")
        trend_dates.append(display_date)

        # 新增用户
        new_user_count = (
            db.query(func.count(User.id))
            .filter(func.date(User.created_at) == d)
            .scalar() or 0
        )
        new_users.append(new_user_count)

        # 活跃用户（有录音记录的不重复用户数）
        active_user_count = (
            db.query(func.count(func.distinct(Record.user_id)))
            .filter(Record.local_date == date_str)
            .scalar() or 0
        )
        active_users.append(active_user_count)

        # 录音数
        record_count = (
            db.query(func.count(Record.id))
            .filter(Record.local_date == date_str)
            .scalar() or 0
        )
        records.append(record_count)

        # 日记数
        diary_count = (
            db.query(func.count(Diary.id))
            .filter(Diary.diary_date == date_str)
            .scalar() or 0
        )
        diaries.append(diary_count)

    trend_7d = {
        "dates": trend_dates,
        "new_users": new_users,
        "active_users": active_users,
        "records": records,
        "diaries": diaries,
    }

    return ApiResponse[dict](
        code=200,
        data={
            "overview": overview,
            "ai_health": ai_health,
            "trend_7d": trend_7d,
        },
    )
