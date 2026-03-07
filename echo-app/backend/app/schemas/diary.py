"""
日记相关 Schema（精简版）
"""
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from datetime import datetime


class DiaryGenerateRequest(BaseModel):
    """生成日记请求"""
    date: str  # YYYY-MM-DD 格式


class CognitiveChangeItem(BaseModel):
    """认知变化项"""
    type: str = ""
    topic: str = ""
    before: str = ""
    after: str = ""
    evidence: str = ""


class CognitiveChange(BaseModel):
    """认知变化"""
    has_change: bool = False
    changes: List[CognitiveChangeItem] = []
    insight: str = ""


class DiaryResponse(BaseModel):
    """日记响应（v3.0 结构化版）"""
    id: str
    user_id: str
    diary_date: str
    # v3.0 字段
    mood_tag: str = "普通的一天"
    emotion_type: str = "neutral"
    keywords: List[str] = []
    what_happened: List[str] = []      # 今天发生了什么
    thoughts: List[str] = []           # 思考碎片
    small_discovery: Optional[str] = None
    closing: str = ""
    tomorrow_hint: Optional[str] = None
    cognitive_change: Optional[Dict[str, Any]] = None
    # 元数据
    record_day_count: int = 0
    generated_at: datetime

    class Config:
        from_attributes = True


class DiaryListResponse(BaseModel):
    """日记列表响应"""
    items: List[DiaryResponse]
    total: int
    page: int
    page_size: int
