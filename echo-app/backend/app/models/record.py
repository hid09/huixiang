"""
语音记录模型
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class VoiceRecord(Base):
    """语音记录表"""
    __tablename__ = "voice_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, comment="用户ID")

    # 音频信息
    audio_url = Column(String(500), nullable=True, comment="语音文件URL")
    audio_duration = Column(Integer, default=0, comment="音频时长（秒）")

    # 转写与分析结果（基础）
    transcribed_text = Column(Text, nullable=True, comment="转写文本")
    primary_emotion = Column(String(20), nullable=True, comment="主导情绪")
    emotion_intensity = Column(Integer, default=5, comment="情绪强度 0-10")
    topic_tags = Column(String(500), nullable=True, comment="话题标签JSON")

    # 增强情绪分析（新增）
    mixed_emotions = Column(String(500), nullable=True, comment="混合情绪JSON: {'开心':6,'疲惫':7}")
    emotion_triggers = Column(String(500), nullable=True, comment="情绪触发事件JSON")
    unspoken_need = Column(String(200), nullable=True, comment="潜在情感需求")
    energy_level = Column(Integer, default=5, comment="能量水平 1-10")
    brief_summary = Column(String(200), nullable=True, comment="一句话概括")

    # 新增：ASR 语音情感 + 输入类型
    asr_emotion = Column(String(20), nullable=True, comment="ASR语音情感: happy/sad/angry/neutral等")
    input_type = Column(String(20), nullable=True, comment="输入类型: 情绪表达/观点分享/事实陈述等")

    # 时间戳
    recorded_at = Column(DateTime, default=datetime.utcnow, comment="记录时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 同步相关
    local_timestamp = Column(DateTime, nullable=True, comment="本地时间戳")
    local_date = Column(String(10), nullable=True, index=True, comment="本地日期 YYYY-MM-DD，用于日记分组")
    sync_status = Column(String(20), default="synced", comment="同步状态")

    def __repr__(self):
        return f"<VoiceRecord {self.id[:8]}...>"
