from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models import User, Record, Diary


class UserService:
    """用户服务"""

    @staticmethod
    def get_users(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Tuple[int, list[dict]]:
        """获取用户列表"""
        query = db.query(User)

        # 搜索过滤（支持用户名和昵称）
        if keyword:
            query = query.filter(
                (User.username.like(f"%{keyword}%")) | (User.name.like(f"%{keyword}%"))
            )

        # 日期过滤
        if start_date:
            query = query.filter(User.created_at >= start_date)
        if end_date:
            query = query.filter(User.created_at <= end_date)

        # 总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        users = query.order_by(desc(User.id)).offset(offset).limit(page_size).all()

        # 补充统计信息（使用一次查询获取所有数据，避免 N+1 问题）
        user_ids = [u.id for u in users]

        # 录音数统计
        records_count = (
            db.query(Record.user_id, func.count(Record.id).label("cnt"))
            .filter(Record.user_id.in_(user_ids))
            .group_by(Record.user_id)
            .all()
        )
        records_count_map = {r.user_id: r.cnt for r in records_count}

        # 日记数统计
        diaries_count = (
            db.query(Diary.user_id, func.count(Diary.id).label("cnt"))
            .filter(Diary.user_id.in_(user_ids))
            .group_by(Diary.user_id)
            .all()
        )
        diaries_count_map = {d.user_id: d.cnt for d in diaries_count}

        # 最后活跃时间（使用子查询一次性获取）
        last_active_subquery = (
            db.query(Record.user_id, func.max(Record.created_at).label("last_active"))
            .filter(Record.user_id.in_(user_ids))
            .group_by(Record.user_id)
            .all()
        )
        last_active_map = {r.user_id: r.last_active for r in last_active_subquery}

        items = []
        for user in users:
            items.append({
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "created_at": user.created_at,
                "records_count": records_count_map.get(user.id, 0),
                "diaries_count": diaries_count_map.get(user.id, 0),
                "last_active": last_active_map.get(user.id),
            })

        return total, items

    @staticmethod
    def get_user_detail(db: Session, user_id: str) -> Optional[dict]:
        """获取用户详情"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # 统计信息
        records_count = db.query(func.count(Record.id)).filter(Record.user_id == user_id).scalar() or 0
        diaries_count = db.query(func.count(Diary.id)).filter(Diary.user_id == user_id).scalar() or 0

        # 最后活跃时间
        last_record = (
            db.query(Record.created_at)
            .filter(Record.user_id == user_id)
            .order_by(desc(Record.created_at))
            .first()
        )
        last_active = last_record.created_at if last_record else None

        # 活跃天数（有录音的不同日期数）
        days_active = (
            db.query(func.count(func.distinct(Record.local_date)))
            .filter(Record.user_id == user_id)
            .scalar() or 0
        )

        return {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "created_at": user.created_at,
            "records_count": records_count,
            "diaries_count": diaries_count,
            "total_voice_count": user.total_voice_count,
            "continuous_days": user.continuous_days,
            "last_active": last_active,
            "days_active": days_active,
        }

    @staticmethod
    def get_user_records(
        db: Session, user_id: str, page: int = 1, page_size: int = 20
    ) -> Tuple[int, list[dict]]:
        """获取用户录音记录"""
        query = db.query(Record).filter(Record.user_id == user_id)
        total = query.count()

        offset = (page - 1) * page_size
        records = query.order_by(desc(Record.created_at)).offset(offset).limit(page_size).all()

        items = []
        for record in records:
            items.append({
                "id": record.id,
                "content": record.transcribed_text,
                "created_at": record.created_at,
                "emotion_type": record.primary_emotion,
                "asr_emotion": record.asr_emotion,
                "mood_tag": record.primary_emotion,  # 使用最终情绪作为心情标签
                "input_type": record.input_type,
            })

        return total, items

    @staticmethod
    def get_user_diaries(
        db: Session, user_id: str, page: int = 1, page_size: int = 20
    ) -> Tuple[int, list[dict]]:
        """获取用户日记记录"""
        query = db.query(Diary).filter(Diary.user_id == user_id)
        total = query.count()

        offset = (page - 1) * page_size
        diaries = query.order_by(desc(Diary.diary_date)).offset(offset).limit(page_size).all()

        items = []
        for diary in diaries:
            # 统计该日记关联的录音数（使用 local_date）
            records_count = (
                db.query(func.count(Record.id))
                .filter(Record.user_id == user_id, Record.local_date == diary.diary_date)
                .scalar() or 0
            )

            items.append({
                "id": diary.id,
                "diary_date": diary.diary_date,
                "emotion_type": diary.emotion_summary,  # emotion_summary 作为 emotion_type
                "mood_tag": diary.mood_tag,
                "keywords": diary.keywords,  # TEXT 类型，前端解析
                "what_happened": diary.events_summary,  # events_summary 作为 what_happened
                "thoughts": diary.thoughts_summary,  # thoughts_summary 作为 thoughts
                "small_discovery": diary.small_discovery,
                "records_count": records_count,
            })

        return total, items

    @staticmethod
    def get_diary_detail(db: Session, diary_id: str) -> Optional[dict]:
        """获取日记详情（含用户信息和关联录音记录）"""
        diary = db.query(Diary).filter(Diary.id == diary_id).first()
        if not diary:
            return None

        # 获取用户信息
        user = db.query(User).filter(User.id == diary.user_id).first()

        # 获取该日记日期的所有录音记录
        records = (
            db.query(Record)
            .filter(
                Record.user_id == diary.user_id,
                Record.local_date == diary.diary_date
            )
            .order_by(Record.created_at)
            .all()
        )

        # 构建响应
        return {
            "id": diary.id,
            "diary_date": diary.diary_date,
            "emotion_type": diary.emotion_summary,
            "mood_tag": diary.mood_tag,
            "keywords": diary.keywords,
            "what_happened": diary.events_summary,
            "thoughts": diary.thoughts_summary,
            "small_discovery": diary.small_discovery,
            "records_count": len(records),
            "user": {
                "id": user.id,
                "username": user.username,
            } if user else None,
            "records": [
                {
                    "id": r.id,
                    "content": r.transcribed_text,
                    "created_at": r.created_at,
                    "emotion_type": r.primary_emotion,
                    "asr_emotion": r.asr_emotion,
                    "mood_tag": None,
                }
                for r in records
            ],
        }
