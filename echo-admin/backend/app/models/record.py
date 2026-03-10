from sqlalchemy import Column, String, Integer, TIMESTAMP, Text

from app.database import Base


class Record(Base):
    """录音记录表（只读，来自回响项目）"""

    __tablename__ = "voice_records"

    id = Column(String(36), primary_key=True)  # UUID 字符串
    user_id = Column(String(36), index=True)
    audio_url = Column(String(500))
    audio_duration = Column(Integer)
    transcribed_text = Column(Text)  # 转录文本
    primary_emotion = Column(String(20))  # 主要情绪
    emotion_intensity = Column(Integer)  # 情绪强度
    topic_tags = Column(String(500))  # 话题标签
    recorded_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP)
    local_date = Column(String(10))  # 本地日期 YYYY-MM-DD
    asr_emotion = Column(String(20))  # ASR 识别的情绪
    input_type = Column(String(20))  # 输入类型

    def __repr__(self):
        return f"<Record(id={self.id}, user_id={self.user_id}, local_date='{self.local_date}')>"
