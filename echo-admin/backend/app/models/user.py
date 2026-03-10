from sqlalchemy import Column, String, Integer, TIMESTAMP

from app.database import Base


class User(Base):
    """用户表（只读，来自回响项目）"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)  # UUID 字符串
    username = Column(String(50))
    name = Column(String(50))  # 用户昵称
    device_id = Column(String(100))
    avatar = Column(String(255))
    timezone = Column(String(50))
    diary_time = Column(String(5))  # 日记生成时间
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    total_record_days = Column(Integer)  # 总记录天数
    total_voice_count = Column(Integer)  # 总录音数
    continuous_days = Column(Integer)  # 连续记录天数
    longest_continuous_days = Column(Integer)  # 最长连续天数
    last_record_date = Column(String(10))  # 最后记录日期

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
