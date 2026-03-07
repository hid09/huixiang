"""
周回顾服务层

功能：
1. 查询本周日记数据（周一到周日）
2. 统计记录天数、语音条数、主导情绪
3. 生成情绪走势（emoji 形式）
4. 提取高频关键词
5. AI 生成下周建议
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from collections import Counter

from app.models.diary import DailyDiary
from app.models.record import VoiceRecord
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


# 情绪类型到 emoji 的映射
EMOTION_EMOJI_MAP = {
    "positive": "😊",
    "neutral": "😌",
    "negative": "😢",
    "mixed": "🤔",
    "none": "·",  # 无记录
}

# 情绪类型到名称的映射
EMOTION_NAME_MAP = {
    "positive": "积极",
    "neutral": "平静",
    "negative": "低落",
    "mixed": "复杂",
    "none": "无记录",
}


def get_week_range(reference_date: Optional[date] = None) -> tuple:
    """
    获取本周的日期范围（周一到周日）

    Args:
        reference_date: 参考日期，默认为今天

    Returns:
        (week_start, week_end) 格式为 "YYYY-MM-DD"
    """
    if reference_date is None:
        reference_date = datetime.now().date()

    # 计算本周一（ISO 周一）
    weekday = reference_date.weekday()  # 0=周一, 6=周日
    week_start = reference_date - timedelta(days=weekday)
    week_end = week_start + timedelta(days=6)

    return week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")


def get_week_dates(week_start: str) -> List[str]:
    """
    获取本周所有日期（周一到周日）

    Args:
        week_start: 周一日期 "YYYY-MM-DD"

    Returns:
        日期列表 ["2024-03-04", "2024-03-05", ...]
    """
    start = datetime.strptime(week_start, "%Y-%m-%d")
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


async def get_weekly_review(db: Session, user_id: str) -> Dict[str, Any]:
    """
    获取本周回顾数据（实时生成）

    数据来源：汇总日记表（daily_diaries）

    Args:
        db: 数据库会话
        user_id: 用户 ID

    Returns:
        周回顾数据结构
    """
    # 1. 获取本周日期范围
    week_start, week_end = get_week_range()
    week_dates = get_week_dates(week_start)
    day_labels = ["一", "二", "三", "四", "五", "六", "日"]

    logger.info(f"生成周回顾: {week_start} ~ {week_end}, user_id={user_id}")

    # 2. 查询本周日记
    diaries = db.query(DailyDiary).filter(
        DailyDiary.user_id == user_id,
        DailyDiary.diary_date >= week_start,
        DailyDiary.diary_date <= week_end
    ).all()

    # 按日期索引
    diary_map = {d.diary_date: d for d in diaries}

    # 3. 查询本周语音条数（从 records 表统计）
    voice_count = db.query(VoiceRecord).filter(
        VoiceRecord.user_id == user_id,
        VoiceRecord.local_date >= week_start,
        VoiceRecord.local_date <= week_end
    ).count()

    # 4. 统计记录天数
    record_days = len(diaries)

    # 5. 统计主导情绪
    emotion_counter = Counter([d.ai_tone for d in diaries if d.ai_tone])
    dominant_emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else "neutral"

    # 6. 构建情绪走势
    emotion_trend = []
    positive_count = 0
    total_valid = 0

    for i, date_str in enumerate(week_dates):
        diary = diary_map.get(date_str)
        if diary and diary.ai_tone:
            emotion_type = diary.ai_tone
            positive_count += 1 if emotion_type == "positive" else 0
            total_valid += 1
        else:
            emotion_type = "none"

        emotion_trend.append({
            "day": day_labels[i],
            "emoji": EMOTION_EMOJI_MAP.get(emotion_type, "·"),
            "emotion_type": emotion_type
        })

    # 7. 计算积极情绪占比
    positive_ratio = round((positive_count / total_valid) * 100) if total_valid > 0 else 0

    # 8. 提取关键词（合并所有日记的 keywords）
    all_keywords = []
    for diary in diaries:
        if diary.keywords:
            try:
                keywords = json.loads(diary.keywords)
                if isinstance(keywords, list):
                    all_keywords.extend(keywords)
            except:
                pass

    # 统计词频
    keyword_counter = Counter(all_keywords)
    top_keywords = keyword_counter.most_common(7)

    # 格式化关键词（前2个为 large）
    keywords_formatted = []
    for i, (text, count) in enumerate(top_keywords):
        keywords_formatted.append({
            "text": text,
            "large": i < 2  # 前两个为大标签
        })

    # 9. AI 生成建议（如果有足够数据）
    suggestions = []
    if len(diaries) >= 1:
        suggestions = await _generate_weekly_suggestions(db, user_id, diaries, week_start, week_end)
    else:
        suggestions = ["开始记录吧，坚持一周就能看到周回顾了！"]

    return {
        "week_start": week_start,
        "week_end": week_end,
        "record_days": record_days,
        "voice_count": voice_count,
        "dominant_emotion": EMOTION_EMOJI_MAP.get(dominant_emotion, "😌"),
        "dominant_emotion_name": EMOTION_NAME_MAP.get(dominant_emotion, "平静"),
        "emotion_trend": emotion_trend,
        "positive_ratio": positive_ratio,
        "keywords": keywords_formatted,
        "suggestions": suggestions
    }


async def _generate_weekly_suggestions(
    db: Session,
    user_id: str,
    diaries: List[DailyDiary],
    week_start: str,
    week_end: str
) -> List[str]:
    """
    使用 AI 生成周回顾建议

    Args:
        db: 数据库会话
        user_id: 用户 ID
        diaries: 本周日记列表
        week_start: 周开始日期
        week_end: 周结束日期

    Returns:
        建议列表
    """
    # 构建日记摘要
    diary_summaries = []
    for d in diaries:
        summary = f"[{d.diary_date}] 情绪: {d.ai_tone or '未知'}"
        if d.keywords:
            try:
                keywords = json.loads(d.keywords)
                summary += f", 关键词: {', '.join(keywords[:3])}"
            except:
                pass
        if d.mood_tag:
            summary += f", 心情: {d.mood_tag}"
        diary_summaries.append(summary)

    prompt = f"""你是"回响"，一个温暖的成长伙伴。根据用户本周的日记记录，给出 2-3 条下周建议。

【本周日记摘要】
{chr(10).join(diary_summaries)}

时间范围：{week_start} 至 {week_end}

【要求】
1. 建议要具体、可执行，不要空话
2. 语气温暖，像朋友聊天
3. 每条建议 30-50 字
4. 如果有积极的行为，鼓励继续
5. 如果有潜在问题，温和提醒

返回 JSON 格式：
{{
    "suggestions": ["建议1", "建议2", "建议3"]
}}
"""

    try:
        from openai import OpenAI
        from app.config import DASHSCOPE_API_KEY

        client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=30.0,
        )

        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )

        content = completion.choices[0].message.content

        # 解析 JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        result = json.loads(content.strip())
        suggestions = result.get("suggestions", [])

        logger.info(f"周回顾建议生成成功: {len(suggestions)} 条")
        return suggestions if suggestions else ["本周记录很棒，下周继续保持！"]

    except Exception as e:
        logger.error(f"生成周回顾建议失败: {e}")
        return ["本周记录很棒，下周继续保持！"]
