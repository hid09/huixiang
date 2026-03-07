"""
记录服务
"""
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.record import VoiceRecord
from app.models.user import User
from app.schemas.record import RecordListResponse
from datetime import datetime, date, timezone, timedelta

# 中国时区
CHINA_TZ = timezone(timedelta(hours=8))


def get_china_now() -> datetime:
    """获取中国时区当前时间"""
    return datetime.now(CHINA_TZ).replace(tzinfo=None)


def get_china_today() -> str:
    """获取中国时区今天的日期字符串 YYYY-MM-DD"""
    return datetime.now(CHINA_TZ).strftime("%Y-%m-%d")


def get_diary_date() -> str:
    """
    获取当前记录应归属的日记日期（6:00-6:00 划分）

    - 6:00-23:59 的记录归属当天
    - 0:00-5:59 的记录归属前一天

    Returns:
        日期字符串 YYYY-MM-DD
    """
    now = datetime.now(CHINA_TZ)
    if now.hour < 6:
        # 凌晨 0-6 点，归入前一天
        yesterday = now - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")
    else:
        # 6 点之后，归入当天
        return now.strftime("%Y-%m-%d")


def _update_user_stats(db: Session, user: User, record_time: datetime):
    """更新用户统计数据"""
    record_date = record_time.strftime("%Y-%m-%d")

    # 更新总语音条数
    user.total_voice_count += 1

    # 检查是否是新的一天记录
    if user.last_record_date != record_date:
        user.total_record_days += 1

        # 计算连续天数
        if user.last_record_date:
            last_date = datetime.strptime(user.last_record_date, "%Y-%m-%d").date()
            today = record_time.date()
            if (today - last_date).days == 1:
                user.continuous_days += 1
            else:
                user.continuous_days = 1
        else:
            user.continuous_days = 1

        # 更新最长连续天数
        if user.continuous_days > user.longest_continuous_days:
            user.longest_continuous_days = user.continuous_days

        user.last_record_date = record_date


def get_record_by_id(db: Session, record_id: str) -> Optional[VoiceRecord]:
    """获取单条记录"""
    return db.query(VoiceRecord).filter(VoiceRecord.id == record_id).first()


def get_month_record_days_by_user_id(db: Session, user_id: str) -> int:
    """根据用户ID获取本月记录天数"""
    today = date.today()
    month_start = today.replace(day=1)

    distinct_dates = db.query(func.date(VoiceRecord.recorded_at)).filter(
        VoiceRecord.user_id == user_id,
        VoiceRecord.recorded_at >= month_start
    ).distinct().count()

    return distinct_dates


# ==================== 基于用户ID的方法（Token认证） ====================

def create_text_record_by_user_id(db: Session, user_id: str, text: str, local_timestamp: datetime = None, local_date: str = None) -> VoiceRecord:
    """创建文字记录（根据用户ID）

    Args:
        local_date: 本地日期字符串 YYYY-MM-DD，用于日记分组
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("用户不存在")

    # 如果没有传入 local_date，使用 6:00-6:00 划分计算日记日期
    if not local_date:
        local_date = get_diary_date()

    record = VoiceRecord(
        user_id=user.id,
        transcribed_text=text,
        recorded_at=local_timestamp or get_china_now(),
        local_timestamp=local_timestamp,
        local_date=local_date
    )
    db.add(record)

    _update_user_stats(db, user, record.recorded_at)

    db.commit()
    db.refresh(record)
    return record


def get_records_by_user_id(db: Session, user_id: str, date_str: str = None, page: int = 1, page_size: int = 20) -> RecordListResponse:
    """获取记录列表（根据用户ID）"""
    query = db.query(VoiceRecord).filter(VoiceRecord.user_id == user_id)

    if date_str:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        query = query.filter(func.date(VoiceRecord.recorded_at) == target_date)

    total = query.count()
    records = query.order_by(VoiceRecord.recorded_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return RecordListResponse(
        items=[record for record in records],
        total=total,
        page=page,
        page_size=page_size
    )


def get_today_records_by_user_id(db: Session, user_id: str) -> List[VoiceRecord]:
    """获取今日所有记录（根据用户ID）

    使用 6:00-6:00 规则计算当前日记日期，确保跨天问题正确处理
    - 凌晨 0:00-5:59 的记录归属前一天（昨晚的日记）
    - 6:00-23:59 的记录归属当天
    """
    # 使用 6:00-6:00 规则获取当前日记日期
    diary_date_str = get_diary_date()
    return db.query(VoiceRecord).filter(
        VoiceRecord.user_id == user_id,
        VoiceRecord.local_date == diary_date_str
    ).order_by(VoiceRecord.recorded_at.asc()).all()


def get_record_by_id_and_user_id(db: Session, record_id: str, user_id: str) -> Optional[VoiceRecord]:
    """获取单条记录（验证用户所有权）"""
    return db.query(VoiceRecord).filter(
        VoiceRecord.id == record_id,
        VoiceRecord.user_id == user_id
    ).first()


def create_voice_record_by_user_id(
    db: Session,
    user_id: str,
    text: str,
    emotion: str = "neutral",
    emotion_score: float = 0.5,
    keywords: List[str] = None,
    topics: List[str] = None,
    audio_duration: int = 0,
    local_timestamp: datetime = None,
    local_date: str = None,
    # 增强情绪分析字段（新增）
    mixed_emotions: Dict[str, int] = None,
    primary_emotion: str = "平静",
    triggers: List[str] = None,
    unspoken_need: str = "",
    energy_level: int = 5,
    brief_summary: str = "",
    # 新增：ASR 语音情感 + 输入类型
    asr_emotion: str = "neutral",
    input_type: str = "情绪表达"
) -> VoiceRecord:
    """
    创建语音记录（包含 AI 分析结果 - 增强版）

    Args:
        db: 数据库会话
        user_id: 用户 ID
        text: 转写文本
        emotion: 情绪类型 (positive/neutral/negative)
        emotion_score: 情绪强度 (0-1)
        keywords: 关键词列表
        topics: 话题标签列表
        audio_duration: 音频时长（秒）
        local_timestamp: 本地时间戳
        local_date: 本地日期 YYYY-MM-DD，用于日记分组（重要！）
        # 增强字段
        mixed_emotions: 混合情绪及强度 {"开心": 6, "疲惫": 7}
        primary_emotion: 具体的主导情绪
        triggers: 情绪触发事件
        unspoken_need: 潜在情感需求
        energy_level: 能量水平 1-10
        brief_summary: 一句话概括
        # 新增字段
        asr_emotion: ASR 语音情感 (happy/sad/angry/neutral等)
        input_type: 输入类型 (情绪表达/观点分享/事实陈述等)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("用户不存在")

    # 计算情绪强度 (0-10)
    emotion_intensity = int(emotion_score * 10)

    # 如果没有传入 local_date，使用 6:00-6:00 划分计算日记日期
    if not local_date:
        local_date = get_diary_date()

    # 将关键词和话题转为 JSON 字符串
    topic_tags_json = json.dumps({
        "keywords": keywords or [],
        "topics": topics or []
    }, ensure_ascii=False)

    # 将混合情绪和触发事件转为 JSON 字符串
    mixed_emotions_json = json.dumps(mixed_emotions or {}, ensure_ascii=False) if mixed_emotions else None
    triggers_json = json.dumps(triggers or [], ensure_ascii=False) if triggers else None

    record = VoiceRecord(
        user_id=user.id,
        transcribed_text=text,
        primary_emotion=primary_emotion or emotion,  # 优先使用具体情绪
        emotion_intensity=emotion_intensity,
        topic_tags=topic_tags_json,
        audio_duration=audio_duration,
        recorded_at=local_timestamp or get_china_now(),
        local_timestamp=local_timestamp,
        local_date=local_date,
        # 增强情绪字段
        mixed_emotions=mixed_emotions_json,
        emotion_triggers=triggers_json,
        unspoken_need=unspoken_need,
        energy_level=energy_level,
        brief_summary=brief_summary,
        # 新增字段
        asr_emotion=asr_emotion,
        input_type=input_type
    )
    db.add(record)

    # 更新用户统计
    _update_user_stats(db, user, record.recorded_at)

    db.commit()
    db.refresh(record)
    return record


def update_record_analysis(
    db: Session,
    record_id: str,
    emotion: str = "neutral",
    emotion_score: float = 0.5,
    keywords: List[str] = None,
    topics: List[str] = None,
    mixed_emotions: Dict[str, int] = None,
    primary_emotion: str = "平静",
    triggers: List[str] = None,
    unspoken_need: str = "",
    energy_level: int = 5,
    brief_summary: str = "",
    # 新增
    input_type: str = "情绪表达"
) -> Optional[VoiceRecord]:
    """
    更新记录的 AI 分析结果（后台异步调用）
    """
    record = db.query(VoiceRecord).filter(VoiceRecord.id == record_id).first()
    if not record:
        return None

    # 更新分析字段
    record.primary_emotion = primary_emotion or emotion
    record.emotion_intensity = int(emotion_score * 10)

    # 更新标签
    record.topic_tags = json.dumps({
        "keywords": keywords or [],
        "topics": topics or []
    }, ensure_ascii=False)

    # 更新增强字段
    record.mixed_emotions = json.dumps(mixed_emotions or {}, ensure_ascii=False) if mixed_emotions else None
    record.emotion_triggers = json.dumps(triggers or [], ensure_ascii=False) if triggers else None
    record.unspoken_need = unspoken_need
    record.energy_level = energy_level
    record.brief_summary = brief_summary

    # 更新新字段
    record.input_type = input_type

    db.commit()
    db.refresh(record)
    return record


def get_records_for_diary(db: Session, user_id: str, target_date_str: str) -> List[Dict]:
    """
    获取指定日期的记录，用于日记生成

    Args:
        target_date_str: 日期字符串 YYYY-MM-DD

    Returns:
        格式化的记录列表 [{"text": "...", "time": "09:30", "emotion": "positive"}, ...]
    """
    records = db.query(VoiceRecord).filter(
        VoiceRecord.user_id == user_id,
        VoiceRecord.local_date == target_date_str
    ).order_by(VoiceRecord.recorded_at.asc()).all()

    result = []
    for r in records:
        result.append({
            "text": r.transcribed_text or "",
            "time": r.recorded_at.strftime("%H:%M") if r.recorded_at else "",
            "emotion": r.primary_emotion or "neutral"
        })

    return result


def get_users_with_records_on_date(db: Session, date_str: str) -> List[str]:
    """
    获取指定日期有记录的所有用户ID

    Args:
        db: 数据库会话
        date_str: 日期字符串 YYYY-MM-DD

    Returns:
        用户ID列表
    """
    # 使用 local_date 字段查询，确保跨天问题正确处理
    user_ids = db.query(VoiceRecord.user_id).filter(
        VoiceRecord.local_date == date_str
    ).distinct().all()

    return [uid[0] for uid in user_ids]
