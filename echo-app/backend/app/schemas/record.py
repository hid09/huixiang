"""
记录相关Schema
"""
from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime


class RecordCreate(BaseModel):
    """创建记录请求（文字版）"""
    text: str
    local_timestamp: Optional[datetime] = None
    local_date: Optional[str] = None  # YYYY-MM-DD，用于日记分组


class VoiceRecordCreate(BaseModel):
    """创建语音记录请求"""
    audio_duration: int = 0
    local_timestamp: Optional[datetime] = None


class TranscribeResponse(BaseModel):
    """转写响应（增强版）"""
    text: str
    # 基础情绪
    emotion: str = "neutral"
    emotion_score: float = 0.5
    # 增强情绪
    mixed_emotions: Dict[str, int] = {}  # {"开心": 6, "疲惫": 7}
    primary_emotion: str = "平静"  # 具体的主导情绪
    triggers: List[str] = []  # 触发事件
    unspoken_need: str = ""  # 潜在需求
    energy_level: int = 5  # 能量水平 1-10
    brief_summary: str = ""  # 一句话概括
    # 标签
    keywords: List[str] = []
    topics: List[str] = []
    # 新增
    input_type: str = "情绪表达"  # 输入类型
    asr_emotion: str = "neutral"  # ASR 语音情感


class RecordResponse(BaseModel):
    """记录响应"""
    id: str
    user_id: str
    transcribed_text: Optional[str] = None
    primary_emotion: Optional[str] = None
    emotion_intensity: int = 5
    topic_tags: Optional[str] = None
    audio_duration: int = 0
    recorded_at: datetime
    created_at: datetime
    local_date: Optional[str] = None  # 本地日期 YYYY-MM-DD，用于日记分组

    class Config:
        from_attributes = True


class RecordListResponse(BaseModel):
    """记录列表响应"""
    items: List[RecordResponse]
    total: int
    page: int
    page_size: int
