from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, Field, field_validator
import json


class UserResponse(BaseModel):
    """用户列表响应"""

    id: str  # UUID string
    username: Optional[str] = None
    name: Optional[str] = None  # 用户昵称
    created_at: datetime
    records_count: int = Field(0, description="录音数量")
    diaries_count: int = Field(0, description="日记数量")
    last_active: Optional[datetime] = Field(None, description="最后活跃时间")

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """用户详情响应"""

    days_active: int = Field(0, description="活跃天数")
    total_voice_count: Optional[int] = Field(None, description="总录音数")
    continuous_days: Optional[int] = Field(None, description="连续记录天数")


class RecordResponse(BaseModel):
    """录音记录响应"""

    id: str  # UUID string
    content: Optional[str] = None
    created_at: datetime
    emotion_type: Optional[str] = None
    asr_emotion: Optional[str] = None
    mood_tag: Optional[str] = None
    input_type: Optional[str] = None

    class Config:
        from_attributes = True


class DiaryResponse(BaseModel):
    """日记响应"""

    id: str  # UUID string
    diary_date: str
    emotion_type: Optional[str] = None
    mood_tag: Optional[str] = None
    keywords: Optional[list] = Field(default_factory=list, description="关键词列表")
    what_happened: Optional[list] = Field(default_factory=list, description="今天发生了什么")
    thoughts: Optional[list] = Field(default_factory=list, description="想法与感悟")
    small_discovery: Optional[str] = None
    records_count: int = Field(0, description="关联录音数量")

    @field_validator('keywords', 'what_happened', 'thoughts', mode='before')
    @classmethod
    def parse_json_fields(cls, v):
        """将JSON字符串转换为list（兼容回响数据库的存储格式）"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    class Config:
        from_attributes = True


class DiaryDetailResponse(DiaryResponse):
    """日记详情响应"""

    user: Optional[dict] = Field(None, description="关联用户信息")
    records: list[RecordResponse] = Field(default_factory=list, description="关联录音记录")
