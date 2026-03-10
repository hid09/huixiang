# Dashboard 相关的 Pydantic 模式
# 由于 dashboard API 返回的是动态字典，这里保留文件以备扩展

from pydantic import BaseModel, Field
from typing import List, Optional


class OverviewStats(BaseModel):
    """概览统计数据"""
    total_users: int
    dau_today: int
    records_today: int
    diaries_today: int


class AIHealth(BaseModel):
    """AI 健康度数据"""
    success_count: int
    fail_count: int
    fail_rate: float


class Trend7D(BaseModel):
    """7天趋势数据"""
    dates: List[str]
    new_users: List[int]
    active_users: List[int]
    records: List[int]
    diaries: List[int]


class DashboardStatsResponse(BaseModel):
    """看板统计数据响应"""
    overview: OverviewStats
    ai_health: AIHealth
    trend_7d: Trend7D
