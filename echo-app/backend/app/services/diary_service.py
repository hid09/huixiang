"""
日记服务
"""
import json
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, date
from app.models.diary import DailyDiary
from app.models.user import User
from app.models.record import VoiceRecord
from app.services.ai_service import ai_service
from app.schemas.diary import DiaryResponse

logger = logging.getLogger(__name__)


def get_diary_by_date(db: Session, user_id: str, diary_date: str) -> Optional[dict]:
    """获取指定日期的日记（返回格式化后的字典）"""
    diary = db.query(DailyDiary).filter(
        DailyDiary.user_id == user_id,
        DailyDiary.diary_date == diary_date
    ).first()
    if diary:
        return _format_diary(diary, db)
    return None


def get_diary_list(db: Session, user_id: str, page: int = 1, page_size: int = 20):
    """获取日记列表"""
    query = db.query(DailyDiary).filter(DailyDiary.user_id == user_id)
    total = query.count()
    diaries = query.order_by(DailyDiary.diary_date.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [_format_diary(d, db) for d in diaries],
        "total": total,
        "page": page,
        "page_size": page_size
    }


async def generate_diary(db: Session, user_id: str, target_date: str) -> Optional[dict]:
    """
    为指定日期生成日记（v1.1 分层生成策略）

    分层策略：
    - 有效记录数 = 0：不生成日记，返回 None
    - 有效记录数 = 1-2：简化版日记（只写 what_happened，thoughts 为空）
    - 有效记录数 ≥ 3：完整版日记（全字段完整生成）

    Args:
        db: 数据库会话
        user_id: 用户 ID
        target_date: 目标日期 YYYY-MM-DD

    Returns:
        生成的日记数据，无有效记录时返回 None
    """
    # 检查是否已存在
    existing = get_diary_by_date(db, user_id, target_date)
    if existing:
        logger.info(f"日记已存在: {target_date}")
        return existing

    # 获取当日有效记录
    records = _get_records_for_date(db, user_id, target_date)

    # 分层生成策略
    if len(records) == 0:
        logger.info(f"无有效记录，不生成日记: {target_date}")
        return None

    # 获取用户统计
    user = db.query(User).filter(User.id == user_id).first()
    record_day_count = user.total_record_days if user else 0

    # 根据有效记录数选择生成策略
    if len(records) <= 2:
        # 简化版生成（1-2条有效记录）
        logger.info(f"简化版生成日记: {target_date}, 记录数: {len(records)}")
        diary_content = await ai_service.generate_simple_diary(records, target_date)
    else:
        # 完整版生成（≥3条有效记录）
        logger.info(f"完整版生成日记: {target_date}, 记录数: {len(records)}")
        diary_content = await ai_service.generate_diary(records, target_date)

    # 检测认知变化（条件触发，只有完整版才检测）
    cognitive_change = None
    if len(records) >= 3:
        cognitive_change = await ai_service.detect_cognitive_change(records)

    # 保存日记（v3.0 结构化版）
    what_happened = diary_content.get("what_happened", [])
    thoughts = diary_content.get("thoughts", [])
    keywords = diary_content.get("keywords", [])

    diary = DailyDiary(
        user_id=user_id,
        diary_date=target_date,
        mood_tag=diary_content.get("mood_tag", ""),
        closing_message=diary_content.get("closing", ""),
        tomorrow_hint=diary_content.get("tomorrow_hint"),
        small_discovery=diary_content.get("small_discovery"),
        thoughts_summary=json.dumps(what_happened, ensure_ascii=False),
        emotion_journey=json.dumps(thoughts, ensure_ascii=False),
        keywords=json.dumps(keywords, ensure_ascii=False) if keywords else None,
        cognitive_change=json.dumps(cognitive_change, ensure_ascii=False) if cognitive_change else None,
        ai_tone=diary_content.get("emotion_type", "neutral"),
        record_day_count=record_day_count
    )

    db.add(diary)
    db.commit()
    db.refresh(diary)

    logger.info(f"日记生成成功: {target_date}, 策略={'简化版' if len(records) <= 2 else '完整版'}, keywords={keywords}")
    return _format_diary(diary, db)


def get_consecutive_empty_days(db: Session, user_id: str) -> int:
    """获取连续未记录天数（供前端首页渐进式关怀使用）

    计算逻辑：
    - 从"当前日记日期"往前数，遇到第一个有日记的日期停止
    - 使用 6:00-6:00 规则判断当前日记日期
    - 最多回溯30天

    优化：一次性查询最近30天的日记，避免 N+1 查询

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        连续未记录天数（今天也算）
    """
    from datetime import timedelta, datetime
    from app.services.record_service import get_diary_date

    # 使用 6:00-6:00 规则获取当前日记日期
    current_diary_date = get_diary_date()
    today = datetime.strptime(current_diary_date, "%Y-%m-%d").date()

    # 计算查询范围：最近30天
    start_date = (today - timedelta(days=29)).strftime("%Y-%m-%d")

    # 一次性查询最近30天的所有日记日期
    diaries = db.query(DailyDiary.diary_date).filter(
        DailyDiary.user_id == user_id,
        DailyDiary.diary_date >= start_date,
        DailyDiary.diary_date <= current_diary_date
    ).all()

    # 存入 Set 便于快速查找
    diary_dates = {d[0] for d in diaries}

    # 在内存中计算连续未记录天数
    count = 0
    for i in range(30):
        check_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if check_date not in diary_dates:
            count += 1
        else:
            break  # 有日记，停止计数

    return count


def _is_valid_record(text: str) -> bool:
    """判断记录是否有效（过滤噪音和测试录音）- 增强版

    过滤规则：
    1. 文本过短（< 4 字符）
    2. 纯语气词/无意义内容
    3. 明显的测试录音
    4. 语义碎片（新增）
    5. 信息量评分过低（新增）
    """
    import re

    if not text or len(text.strip()) < 4:
        return False

    text = text.strip()

    # 去除标点后检查
    text_no_punct = re.sub(r'[，。！？、；：""''（）\.\!\?\,\;:\(\)\s]', '', text)

    if len(text_no_punct) < 3:
        return False

    # 过滤纯语气词（嗯、啊、哼、哈等重复组合）
    pure_noise_chars = set('嗯啊哦额唔哼哈呵嘿嗨喂噢哎耶')
    if all(c in pure_noise_chars for c in text_no_punct):
        return False

    # 过滤纯重复字符（如 "哈哈哈哈"、"嗯嗯嗯"）
    if len(set(text_no_punct)) == 1 and len(text_no_punct) <= 10:
        return False

    # 过滤纯英文测试词
    text_lower = text.strip().lower()
    test_words = ["hello", "hello hello", "hellou", "hi", "test", "ok", "okok", "hellohello"]
    if text_lower in test_words or text_lower.replace(" ", "") in test_words:
        return False

    # 过滤明显是测试的句子
    test_patterns = ["能听到", "这是什么", "录什么", "喂喂喂", "起开滚", "起开，滚"]
    for pattern in test_patterns:
        if pattern in text:
            return False

    # 新增：语义碎片检测
    if _is_semantic_fragment(text):
        return False

    # 新增：信息量评分（过滤掉评分过低的）
    if _calc_info_score(text) < 2:
        return False

    return True


def _is_semantic_fragment(text: str) -> bool:
    """检测是否是语义碎片（不完整的句子）"""
    import re

    text = text.strip()

    # 动词后无宾语的模式
    incomplete_patterns = [
        r'^(今天|刚才|刚刚)(做了|看了|听了|吃了|去了|说了|想了)$',
        r'^(昨天|前天)(做了|看了|听了|吃了|去了)$',
        r'^.{1,3}(了|着|过)$',  # 单独的动词后缀
    ]
    for pattern in incomplete_patterns:
        if re.match(pattern, text):
            return True

    # 纯名词/人名（2-4字，无动词）
    noun_only = re.match(r'^[a-zA-Z\u4e00-\u9fa5]{2,4}$', text)
    if noun_only and not any(v in text for v in ['是', '有', '做', '去', '来', '说', '想', '看', '听', '吃', '玩', '买', '用', '给', '让', '把', '被', '会', '能', '要', '在', '到', '从', '向', '对', '和', '跟', '与', '及', '或', '但', '可', '因', '所', '而', '才', '就', '也', '都', '还', '又', '再', '不', '没', '很', '太', '好', '多', '少', '大', '小', '高', '低', '快', '慢', '早', '晚', '长', '短', '新', '旧', '老', '真', '假', '对', '错']):
        # 排除一些常见的有意义短语
        exclude = ['老朋友', '新朋友', '好心情', '晚安', '早安', '谢谢', '对不起', '不好意思']
        if text not in exclude:
            return True

    return False


def _calc_info_score(text: str) -> int:
    """计算信息量评分 0-10

    评分标准：
    - 长度：越长信息量越大
    - 完整句子：有标点符号加分
    - 情感词：有情绪表达加分
    - 事件要素：有人/事/物加分
    - 行为描述：有具体动作加分
    """
    score = 0

    # 长度加分
    if len(text) >= 6:
        score += 1
    if len(text) >= 10:
        score += 1
    if len(text) >= 20:
        score += 1

    # 有完整句子加分（标点符号）
    if '，' in text or '。' in text or '！' in text or '？' in text:
        score += 2

    # 有情感词加分
    emotion_words = ['开心', '高兴', '快乐', '兴奋', '满足', '期待', '感激',
                     '累', '烦', '焦虑', '低落', '愤怒', '失望', '孤独', '压力',
                     '平静', '轻松', '舒服', '不错', '挺好', '还好', '好']
    if any(w in text for w in emotion_words):
        score += 2

    # 有事件要素加分
    event_words = ['朋友', '同事', '家人', '老板', '客户', '会议', '项目', '工作',
                   '吃饭', '聚餐', '跑步', '运动', '健身', '读书', '学习', '睡觉',
                   '今天', '昨天', '明天', '上午', '下午', '晚上', '凌晨', '中午',
                   '火锅', '奶茶', '咖啡', '饭', '菜']
    if any(w in text for w in event_words):
        score += 1

    # 有具体行为/状态描述
    action_patterns = ['去', '来', '做', '看', '听', '吃', '买', '用', '想', '说', '觉得', '发现', '意识到']
    if any(p in text for p in action_patterns):
        score += 1

    # 有时间描述
    time_patterns = ['早上', '中午', '下午', '晚上', '凌晨', '今天', '昨天', '明天']
    if any(p in text for p in time_patterns):
        score += 1

    # 纯碎片减分
    if len(set(text)) <= 3 and len(text) <= 6:
        score -= 3

    return max(0, min(10, score))


def _get_records_for_date(db: Session, user_id: str, date_str: str) -> List[dict]:
    """获取指定日期的所有记录，格式化为 AI 生成所需格式

    查询逻辑：
    1. 优先使用 local_date 字段（6:00-6:00 划分）
    2. 如果 local_date 为空，在 Python 层面用 6:00-6:00 规则计算归属日期
    3. 过滤掉无效的测试/噪音记录
    """
    from datetime import timedelta
    from sqlalchemy import or_

    # 计算相邻日期（用于 6:00-6:00 规则的兜底计算）
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    prev_date = (target_date - timedelta(days=1)).strftime("%Y-%m-%d")
    next_date = (target_date + timedelta(days=1)).strftime("%Y-%m-%d")

    # 查询可能相关的记录（local_date 匹配，或 local_date 为空且 recorded_at 在前后两天内）
    records = db.query(VoiceRecord).filter(
        VoiceRecord.user_id == user_id,
        or_(
            VoiceRecord.local_date == date_str,
            and_(
                VoiceRecord.local_date.is_(None),
                VoiceRecord.recorded_at >= target_date - timedelta(days=1),
                VoiceRecord.recorded_at < target_date + timedelta(days=2)
            )
        )
    ).order_by(VoiceRecord.recorded_at.asc()).all()

    # 过滤出真正属于目标日期的记录
    result = []
    for r in records:
        # 如果 local_date 存在且匹配，直接使用
        if r.local_date == date_str:
            result.append(r)
            continue

        # 如果 local_date 为空，用 6:00-6:00 规则计算
        if r.local_date is None and r.recorded_at:
            recorded_date = r.recorded_at.date()
            hour = r.recorded_at.hour

            # 6:00-23:59 归属当天，0:00-5:59 归属前一天
            if hour >= 6:
                calc_date = recorded_date.strftime("%Y-%m-%d")
            else:
                calc_date = (recorded_date - timedelta(days=1)).strftime("%Y-%m-%d")

            if calc_date == date_str:
                result.append(r)

    # 格式化并过滤无效记录
    formatted_records = []
    for r in result:
        text = r.transcribed_text or ""
        if _is_valid_record(text):
            formatted_records.append({
                "text": text,
                "time": r.recorded_at.strftime("%H:%M") if r.recorded_at else "",
                "emotion": r.primary_emotion or "neutral"
            })

    return formatted_records


def _format_diary(diary: DailyDiary, db: Session = None) -> dict:
    """格式化日记响应（v3.0 结构化版）

    字段映射：
    - thoughts_summary -> what_happened
    - emotion_journey -> thoughts
    - small_discovery -> small_discovery
    """
    # 解析 what_happened（存放在 thoughts_summary 字段）
    what_happened = []
    try:
        if diary.thoughts_summary:
            what_happened = json.loads(diary.thoughts_summary)
    except:
        pass

    # 解析 thoughts（存放在 emotion_journey 字段）
    thoughts = []
    try:
        if diary.emotion_journey:
            thoughts = json.loads(diary.emotion_journey)
    except:
        pass

    # 解析 keywords
    keywords = []
    try:
        if diary.keywords:
            keywords = json.loads(diary.keywords)
    except:
        pass

    # 解析 cognitive_change
    cognitive_change = None
    try:
        if diary.cognitive_change:
            cognitive_change = json.loads(diary.cognitive_change)
    except:
        pass

    return {
        "id": diary.id,
        "user_id": diary.user_id,
        "diary_date": diary.diary_date,
        # v3.0 字段
        "mood_tag": diary.mood_tag or "普通的一天",
        "emotion_type": diary.ai_tone or "neutral",
        "keywords": keywords,
        "what_happened": what_happened,
        "thoughts": thoughts,
        "small_discovery": diary.small_discovery,
        "closing": diary.closing_message or "",
        "tomorrow_hint": diary.tomorrow_hint,
        "cognitive_change": cognitive_change,
        # 元数据
        "record_day_count": diary.record_day_count,
        "generated_at": diary.generated_at
    }
