"""
日记模型
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class DailyDiary(Base):
    """每日日记表"""
    __tablename__ = "daily_diaries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True, comment="用户ID")

    # 日期（唯一）
    diary_date = Column(String(10), unique=False, index=True, comment="日记日期 YYYY-MM-DD")

    # 日记内容（基础）
    emotion_summary = Column(Text, nullable=True, comment="情绪总结")
    events_summary = Column(Text, nullable=True, comment="事件总结")
    thoughts_summary = Column(Text, nullable=True, comment="思考总结")
    small_discovery = Column(Text, nullable=True, comment="小发现")
    emotion_journey = Column(Text, nullable=True, comment="情绪旅程")
    closing_message = Column(Text, nullable=True, comment="结束语")

    # 日记内容（故事化新增）
    story = Column(Text, nullable=True, comment="故事化描述")
    reflection = Column(Text, nullable=True, comment="思考/反思")
    highlight = Column(Text, nullable=True, comment="高光时刻")
    mood_tag = Column(String(50), nullable=True, comment="心情标签")
    tomorrow_hint = Column(Text, nullable=True, comment="明日提示")
    keywords = Column(Text, nullable=True, comment="关键词JSON数组")
    cognitive_change = Column(Text, nullable=True, comment="认知变化JSON")

    # AI相关
    ai_tone = Column(String(20), default="calm", comment="AI使用的语气")

    # 记录天数
    record_day_count = Column(Integer, default=0, comment="第几天记录")

    # 时间戳
    generated_at = Column(DateTime, default=datetime.utcnow, comment="生成时间")

    def __repr__(self):
        return f"<DailyDiary {self.diary_date}>"
