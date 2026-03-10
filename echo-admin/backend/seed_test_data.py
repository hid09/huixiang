#!/usr/bin/env python3
"""
创建测试数据脚本
"""
import sys
import os
import random
import json
import uuid
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Record, Diary, AdminUser
from app.utils.password import get_password_hash


def create_test_data():
    """创建测试数据"""
    # 使用 SQLite 数据库
    DATABASE_URL = "sqlite:///./echo_admin.db"
    print(f"使用数据库: {DATABASE_URL}")

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 创建所有表
        print("初始化数据库表...")
        Base.metadata.create_all(bind=engine)

        # 创建管理员账号
        print("创建管理员账号...")
        admin_exists = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin_exists:
            admin = AdminUser(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role="super",
            )
            db.add(admin)
            db.commit()
            print("  ✓ 超级管理员创建成功: admin / admin123")
        else:
            print("  - 管理员账号已存在")

        # 清空旧测试数据
        print("\n清空旧测试数据...")
        db.query(Diary).delete()
        db.query(Record).delete()
        db.query(User).delete()
        db.commit()

        # 创建测试用户
        print("创建测试用户...")
        import uuid
        users = []
        for i in range(1, 11):
            user = User(
                id=str(uuid.uuid4()),
                username=f"user{i:03d}",
                created_at=datetime.now() - timedelta(days=i*10),
                total_record_days=i*5,
                total_voice_count=i*10,
                continuous_days=i % 7,
            )
            db.add(user)
            users.append(user)
        db.commit()

        # 刷新以获取 ID
        for user in users:
            db.refresh(user)

        # 创建测试录音记录
        print("创建测试录音记录...")
        records = []
        emotions = ['positive', 'neutral', 'negative', 'mixed']
        asr_emotions = ['happy', 'neutral', 'sad', 'angry']
        mood_tags = ['开心', '平静', '疲惫', '焦虑']
        input_types = ['情绪表达', '观点分享', '事实陈述']

        for idx, user in enumerate(users):
            # 每个用户创建 5-15 条录音记录
            num_records = 5 + (idx % 10)
            for j in range(num_records):
                record = Record(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    transcribed_text=f"这是用户{user.username}的第{j+1}条录音内容，记录了一些想法和感受。",
                    created_at=datetime.now() - timedelta(days=j*2, hours=j*3),
                    primary_emotion=emotions[j % len(emotions)],
                    emotion_intensity=int(50 + (j % 5) * 10),
                    asr_emotion=asr_emotions[j % len(asr_emotions)],
                    topic_tags=mood_tags[j % len(mood_tags)],
                    input_type=input_types[j % len(input_types)],
                    local_date=(datetime.now() - timedelta(days=j*2)).strftime('%Y-%m-%d')
                )
                db.add(record)
                records.append(record)
        db.commit()

        # 刷新以获取 ID
        for record in records:
            db.refresh(record)

        # 创建测试日记
        print("创建测试日记...")
        diary_by_user = {}
        for idx, user in enumerate(users):
            # 每个用户创建 2-5 篇日记
            num_diaries = 2 + (idx % 4)
            for j in range(num_diaries):
                diary = Diary(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    diary_date=(datetime.now() - timedelta(days=j*3)).strftime('%Y-%m-%d'),
                    emotion_summary=emotions[j % len(emotions)],
                    mood_tag=mood_tags[j % len(mood_tags)],
                    events_summary=f"今天做了一些有趣的事情，比如学习新技能。和朋友聊天，分享了一些想法。",
                    thoughts_summary=f"感觉今天过得很充实。希望能保持这样的状态。",
                    small_discovery=f"发现保持积极心态很重要（用户{idx+1}日记{j+1}）",
                    keywords=json.dumps(["学习", "成长", "心态"]),
                    cognitive_change=json.dumps({
                        "before": "有些焦虑",
                        "after": "更加平静",
                        "insight": "通过记录和反思，能够更好地认识自己"
                    }),
                    record_day_count=idx + 1,
                    generated_at=datetime.now() - timedelta(days=j*3)
                )
                db.add(diary)
                diary_by_user[diary] = j + 1
        db.commit()

        print("=" * 50)
        print("测试数据创建成功！")
        print("=" * 50)
        print(f"创建用户数: {len(users)}")
        print(f"创建录音记录数: {len(records)}")
        print(f"创建日记数: {len(diary_by_user)}")
        print("=" * 50)

        # 打印统计信息
        total_users = db.query(User).count()
        total_records = db.query(Record).count()
        total_diaries = db.query(Diary).count()
        print(f"数据库中用户总数: {total_users}")
        print(f"数据库中录音总数: {total_records}")
        print(f"数据库中日记总数: {total_diaries}")
        print("=" * 50)

    except Exception as e:
        print(f"创建失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
