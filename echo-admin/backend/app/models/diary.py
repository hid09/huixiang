from sqlalchemy import Column, String, Integer, TIMESTAMP, Text

from app.database import Base


class Diary(Base):
    """日记表（只读，来自回响项目）"""

    __tablename__ = "daily_diaries"

    id = Column(String(36), primary_key=True)  # UUID 字符串
    user_id = Column(String(36), index=True)
    diary_date = Column(String(10))  # 日记日期 YYYY-MM-DD
    emotion_summary = Column(Text)  # 情绪总结
    events_summary = Column(Text)  # 事件总结（今天发生了什么）
    thoughts_summary = Column(Text)  # 想法与感悟
    small_discovery = Column(Text)  # 小发现
    emotion_journey = Column(Text)  # 情绪旅程
    closing_message = Column(Text)  # 结语
    ai_tone = Column(String(20))  # AI 语气
    record_day_count = Column(Integer)  # 记录天数
    generated_at = Column(TIMESTAMP)  # 生成时间
    story = Column(Text)  # 故事
    reflection = Column(Text)  # 反思
    highlight = Column(Text)  # 亮点
    mood_tag = Column(String(50))  # 心情标签
    tomorrow_hint = Column(Text)  # 明日提示
    keywords = Column(Text)  # 关键词（JSON 字符串）
    cognitive_change = Column(Text)  # 认知变化（JSON 字符串）

    def __repr__(self):
        return f"<Diary(id={self.id}, user_id={self.user_id}, diary_date='{self.diary_date}')>"
