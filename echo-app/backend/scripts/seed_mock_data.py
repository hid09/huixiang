"""
Mock数据生成脚本
运行方式：cd backend && python scripts/seed_mock_data.py
"""
import sys
import os
# 将backend目录添加到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.record import VoiceRecord
from app.models.diary import DailyDiary
from app.core.auth import hash_password

# 创建所有表
Base.metadata.create_all(bind=engine)

# Mock数据模板
EMOTIONS = ['开心', '平静', '焦虑', '低落', '兴奋', '满足', '疲惫']
EMOTION_EMOJIS = {'开心': '😊', '平静': '😌', '焦虑': '😰', '低落': '😔', '兴奋': '🤩', '满足': '😌', '疲惫': '😴'}

# 语音记录模板
RECORD_TEMPLATES = [
    {"text": "今天开会时发现自己不再像以前那样紧张了，感觉变得自信了一些。项目进展顺利，团队配合得很好。", "emotion": "满足", "tags": ["工作", "成长", "团队"]},
    {"text": "晚上去跑步了，空气很好，久违的放松。跑了5公里，感觉身体状态在慢慢恢复。", "emotion": "开心", "tags": ["运动", "健康"]},
    {"text": "读了一会儿书，《被讨厌的勇气》里有些观点让我深思。关于课题分离的概念，好像解答了我最近的困惑。", "emotion": "平静", "tags": ["读书", "思考"]},
    {"text": "今天有点累，开了三个会，脑子一直在转。回家后只想躺着，什么都不想做。", "emotion": "疲惫", "tags": ["工作", "压力"]},
    {"text": "和朋友聊了聊最近的困惑，他说的一些话让我豁然开朗。有时候换个角度看问题，真的会有不一样的发现。", "emotion": "开心", "tags": ["朋友", "社交", "思考"]},
    {"text": "项目上线了！忙了两周终于看到成果，虽然过程很辛苦，但是很有成就感。", "emotion": "兴奋", "tags": ["工作", "成就"]},
    {"text": "今天状态不太好，可能是昨晚睡太晚了。感觉有些焦虑，担心下周的deadline。", "emotion": "焦虑", "tags": ["工作", "压力"]},
    {"text": "和家人视频通话了，聊了很多。虽然隔着屏幕，但感觉很温暖。", "emotion": "开心", "tags": ["家人", "温暖"]},
    {"text": "今天天气很好，中午出去走了走，阳光照在身上很舒服。简单的幸福。", "emotion": "平静", "tags": ["生活", "放松"]},
    {"text": "学了一个新的技术框架，感觉很有意思。虽然开始有点难，但是慢慢上手了。", "emotion": "满足", "tags": ["学习", "成长"]},
    {"text": "今天被客户批评了，心里有点难受。不过冷静下来想想，确实有些地方可以做得更好。", "emotion": "低落", "tags": ["工作", "反思"]},
    {"text": "早起看日出，很久没有这样安静地待着了。新的一天，充满希望。", "emotion": "平静", "tags": ["生活", "希望"]},
]

# 日记模板
DIARY_TEMPLATES = [
    {
        "emotion_summary": "平静中带着一点期待。早上有些许紧张，但下午逐渐放松下来。",
        "events_summary": "• 早上开会时发现自己不再像以前那样紧张了\n• 晚上跑步时想到了一个新的项目点子\n• 和同事讨论了下周的方案，有了新的思路",
        "thoughts_summary": "\"原来紧张是因为太在意别人的看法，现在更在意自己的判断\"",
        "small_discovery": "你提到\"跑步\"时，情绪是积极的，这已经是本周第3次。运动似乎是你调节情绪的重要方式。",
        "closing_message": "明天见，记得照顾好自己 ☀️"
    },
    {
        "emotion_summary": "忙碌但充实的一天。上午有些焦虑，下午逐渐找到节奏。",
        "events_summary": "• 项目顺利上线，团队配合超棒\n• 收到了客户的正面反馈\n• 晚上和朋友聚餐，聊了很多",
        "thoughts_summary": "\"忙碌不可怕，可怕的是没有方向的忙碌\"",
        "small_discovery": "你今天提到了3次\"感谢\"，感恩的心态正在成为你的习惯。",
        "closing_message": "辛苦了，今晚好好休息 🌙"
    },
    {
        "emotion_summary": "有些低落，但也有温暖的时刻。情绪像天气一样，会过去。",
        "events_summary": "• 上午被客户批评，心里有些难受\n• 中午出去走了走，阳光让心情好了一些\n• 晚上看了一部喜欢的电影",
        "thoughts_summary": "\"被批评不代表我不够好，只是有些地方可以做得更好\"",
        "small_discovery": "你在低落时会主动寻找让自己感觉好的事情，这是一种自我调节的能力。",
        "closing_message": "抱抱自己，明天是新的一天 🌈"
    }
]

def generate_mock_data(db: Session, user_id: str):
    """生成mock数据"""
    now = datetime.now()

    # 生成最近14天的语音记录
    records = []
    for day_offset in range(14):
        date = now - timedelta(days=day_offset)

        # 每天1-3条记录
        daily_records = random.sample(RECORD_TEMPLATES, random.randint(1, 3))

        for i, template in enumerate(daily_records):
            # 随机时间 8:00 - 22:00
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            record_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            record = VoiceRecord(
                user_id=user_id,
                transcribed_text=template["text"],
                primary_emotion=template["emotion"],
                emotion_intensity=random.randint(4, 8),
                topic_tags=",".join(template["tags"]),
                audio_duration=random.randint(15, 120),
                recorded_at=record_time,
                created_at=record_time
            )
            records.append(record)
            db.add(record)

    db.commit()
    print(f"✅ 已生成 {len(records)} 条语音记录")

    # 生成最近7天的日记
    diaries = []
    for day_offset in range(7):
        date = now - timedelta(days=day_offset)
        date_str = date.strftime("%Y-%m-%d")

        template = random.choice(DIARY_TEMPLATES)

        diary = DailyDiary(
            user_id=user_id,
            diary_date=date_str,
            emotion_summary=template["emotion_summary"],
            events_summary=template["events_summary"],
            thoughts_summary=template["thoughts_summary"],
            small_discovery=template["small_discovery"],
            closing_message=template["closing_message"],
            ai_tone="calm",
            record_day_count=14 - day_offset,
            generated_at=date.replace(hour=22, minute=30, second=0, microsecond=0)
        )
        diaries.append(diary)
        db.add(diary)

    db.commit()
    print(f"✅ 已生成 {len(diaries)} 条日记")

    # 更新用户统计
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.total_record_days = 14
        user.total_voice_count = len(records)
        user.continuous_days = 14
        user.longest_continuous_days = 14
        user.last_record_date = now.strftime("%Y-%m-%d")
        db.commit()
        print(f"✅ 已更新用户统计")

    return records, diaries

def main():
    db: Session = SessionLocal()
    try:
        # 查找或创建测试用户
        test_username = "testuser"
        user = db.query(User).filter(User.username == test_username).first()

        if not user:
            user = User(
                username=test_username,
                password_hash=hash_password("123456"),
                name="测试用户"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ 创建测试用户: {test_username}")
        else:
            # 清除旧数据
            db.query(VoiceRecord).filter(VoiceRecord.user_id == user.id).delete()
            db.query(DailyDiary).filter(DailyDiary.user_id == user.id).delete()
            print(f"✅ 清除旧数据")

        # 生成mock数据
        generate_mock_data(db, user.id)

        print("\n🎉 Mock数据生成完成！")
        print(f"📝 测试账号: {test_username}")
        print(f"🔑 测试密码: 123456")

    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
