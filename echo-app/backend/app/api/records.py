"""
记录相关API
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, Dict
import json
import logging
import time
from app.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.record import RecordCreate, RecordResponse, RecordListResponse, TranscribeResponse
from app.services import record_service
from app.services.ai_service import ai_service
from app.core.deps import get_current_user, get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/api/records", tags=["记录"])
logger = logging.getLogger(__name__)


@router.post("/text", response_model=ApiResponse[RecordResponse])
async def create_text_record(
    request: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建文字记录（需要认证）

    MVP版本：暂时不调用AI，直接保存记录
    """
    # 校验文本不能为空
    if not request.text or not request.text.strip():
        return ApiResponse(
            success=False,
            data=None,
            message="请输入内容"
        )
    
    record = record_service.create_text_record_by_user_id(
        db, current_user.id, request.text, request.local_timestamp, request.local_date
    )
    return ApiResponse(
        data=RecordResponse.model_validate(record),
        message="记录成功"
    )


@router.get("", response_model=ApiResponse[RecordListResponse])
async def get_records(
    current_user: User = Depends(get_current_user),
    date_str: str = Query(None, alias="date", description="筛选日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """获取记录列表（需要认证）"""
    result = record_service.get_records_by_user_id(
        db, current_user.id, date_str, page, page_size
    )
    return ApiResponse(data=result)


@router.get("/today", response_model=ApiResponse[list[RecordResponse]])
async def get_today_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取今日所有记录（需要认证）"""
    t_start = time.time()
    records = record_service.get_today_records_by_user_id(db, current_user.id)
    t_end = time.time()
    print(f"📋 [/records/today] 耗时: {t_end-t_start:.2f}秒, 记录数: {len(records)}", flush=True)
    return ApiResponse(
        data=[RecordResponse.model_validate(r) for r in records]
    )


@router.get("/{record_id}", response_model=ApiResponse[RecordResponse])
async def get_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单条记录详情（需要认证）"""
    record = record_service.get_record_by_id_and_user_id(db, record_id, current_user.id)
    if not record:
        return ApiResponse(
            success=False,
            data=None,
            message="记录不存在"
        )
    return ApiResponse(data=RecordResponse.model_validate(record))


# ==================== 语音相关 API ====================

@router.post("/voice/transcribe", response_model=ApiResponse[TranscribeResponse])
async def transcribe_voice(
    audio: UploadFile = File(..., description="音频文件"),
    current_user: User = Depends(get_current_user)
):
    """
    语音转写（快速版 - 只做ASR，不做文本分析）

    接收音频文件，只返回转写文本和ASR情感
    文本分析延迟到确认发送时再进行
    """
    try:
        # 读取音频文件
        audio_content = await audio.read()
        file_ext = audio.filename.split(".")[-1] if audio.filename and "." in audio.filename else "webm"

        logger.info(f"收到语音文件: {audio.filename}, 大小: {len(audio_content)} bytes, 格式: {file_ext}")

        # 调用 AI 转写（返回 dict，含 text 和 asr_emotion）
        asr_result = await ai_service.transcribe_audio_file(audio_content, file_ext)
        transcribed_text = asr_result.get("text")
        asr_emotion = asr_result.get("asr_emotion", "neutral")

        if not transcribed_text:
            return ApiResponse(
                success=False,
                data=None,
                message="语音转写失败，请重试"
            )

        # 不再调用文本分析，直接返回文字和ASR情感
        return ApiResponse(
            data=TranscribeResponse(
                text=transcribed_text,
                # 情绪字段用默认值，确认发送时再分析
                emotion="neutral",
                emotion_score=0.5,
                mixed_emotions={},
                primary_emotion="平静",
                triggers=[],
                unspoken_need="",
                energy_level=5,
                brief_summary="",
                keywords=[],
                topics=[],
                input_type="待分析",
                asr_emotion=asr_emotion
            ),
            message="转写成功"
        )

    except Exception as e:
        logger.error(f"语音转写失败: {e}")
        return ApiResponse(
            success=False,
            data=None,
            message=f"转写失败: {str(e)}"
        )


@router.post("/voice/confirm", response_model=ApiResponse[RecordResponse])
async def confirm_voice_record(
    background_tasks: BackgroundTasks,
    request: RecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    确认语音记录（异步版 - 快速响应）

    1. 接收编辑后的文本
    2. 先保存记录（情绪="分析中"），立即返回
    3. 后台异步执行情绪分析，完成后更新记录
    """
    try:
        # 解析本地时间
        local_dt = None
        if request.local_timestamp:
            try:
                local_dt = datetime.fromisoformat(request.local_timestamp.replace("Z", "+00:00"))
            except:
                local_dt = datetime.utcnow()

        # 先创建记录（情绪标记为"分析中"），立即返回
        record = record_service.create_voice_record_by_user_id(
            db=db,
            user_id=current_user.id,
            text=request.text,
            emotion="neutral",  # 临时值
            emotion_score=0.5,
            keywords=[],
            topics=[],
            audio_duration=0,
            local_timestamp=local_dt,
            local_date=request.local_date,
            mixed_emotions={},
            primary_emotion="分析中",  # 标记为分析中
            triggers=[],
            unspoken_need="",
            energy_level=5,
            brief_summary="",
            input_type="分析中"
        )

        logger.info(f"✅ 记录创建成功，ID: {record.id}，启动后台分析任务")

        # 后台异步执行情绪分析
        async def analyze_and_update():
            """后台任务：分析情绪并更新记录"""
            try:
                from app.database import SessionLocal
                db_bg = SessionLocal()

                t_start = time.time()
                print(f"🧠 [后台分析] 开始分析记录 {record.id}, 文本: {request.text[:30]}...", flush=True)

                analysis = await ai_service.analyze_record(request.text)

                t_end = time.time()
                print(f"🧠 [后台分析] 分析完成，耗时: {t_end-t_start:.2f}秒", flush=True)

                # 更新记录
                record_service.update_record_analysis(
                    db=db_bg,
                    record_id=record.id,
                    emotion=analysis.get("emotion", "neutral"),
                    emotion_score=analysis.get("emotion_score", 0.5),
                    keywords=analysis.get("keywords", []),
                    topics=analysis.get("topics", []),
                    mixed_emotions=analysis.get("mixed_emotions"),
                    primary_emotion=analysis.get("primary_emotion", "平静"),
                    triggers=analysis.get("triggers"),
                    unspoken_need=analysis.get("unspoken_need", ""),
                    energy_level=analysis.get("energy_level", 5),
                    brief_summary=analysis.get("brief_summary", ""),
                    input_type=analysis.get("input_type", "情绪表达")
                )
                logger.info(f"✅ [后台] 记录分析更新完成，ID: {record.id}")
                db_bg.close()
            except Exception as e:
                logger.error(f"❌ [后台] 分析任务失败: {e}")

        background_tasks.add_task(analyze_and_update)

        return ApiResponse(
            data=RecordResponse.model_validate(record),
            message="记录成功"
        )

    except Exception as e:
        logger.error(f"确认语音记录失败: {e}")
        return ApiResponse(
            success=False,
            data=None,
            message=f"记录失败: {str(e)}"
        )


@router.post("/voice", response_model=ApiResponse[RecordResponse])
async def create_voice_record(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(..., description="音频文件"),
    audio_duration: int = Form(0, description="音频时长（秒）"),
    local_timestamp: Optional[str] = Form(None, description="本地时间戳"),
    local_date: Optional[str] = Form(None, description="本地日期 YYYY-MM-DD"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建语音记录（优化版 - 快速响应）

    1. 接收音频文件
    2. 调用 AI 转写（同步，必须等待）
    3. 先创建基础记录并立即返回
    4. 后台异步执行情绪分析，完成后更新记录
    """
    try:
        # 读取音频文件
        audio_content = await audio.read()
        file_ext = audio.filename.split(".")[-1] if audio.filename and "." in audio.filename else "webm"

        logger.info(f"🎤 收到语音文件: {audio.filename}, 大小: {len(audio_content)/1024:.1f} KB, 时长: {audio_duration}秒")

        # 1. 调用 AI 转写（返回 dict，含 text 和 asr_emotion）
        t0 = time.time()
        asr_result = await ai_service.transcribe_audio_file(audio_content, file_ext)
        transcribed_text = asr_result.get("text")
        asr_emotion = asr_result.get("asr_emotion", "neutral")
        t1 = time.time()
        logger.info(f"⏱️ ASR转写耗时: {t1-t0:.2f}秒, ASR情感: {asr_emotion}")

        if not transcribed_text:
            return ApiResponse(
                success=False,
                data=None,
                message="语音转写失败，请重试"
            )

        # 2. 解析本地时间戳
        local_dt = None
        if local_timestamp:
            try:
                local_dt = datetime.fromisoformat(local_timestamp.replace("Z", "+00:00"))
            except:
                local_dt = datetime.utcnow()

        # 3. 先创建基础记录（不含分析结果），立即返回
        record = record_service.create_voice_record_by_user_id(
            db=db,
            user_id=current_user.id,
            text=transcribed_text,
            emotion="neutral",  # 临时值，后台分析后更新
            emotion_score=0.5,
            keywords=[],
            topics=[],
            audio_duration=audio_duration,
            local_timestamp=local_dt,
            local_date=local_date,
            mixed_emotions={},
            primary_emotion="分析中",
            triggers=[],
            unspoken_need="",
            energy_level=5,
            brief_summary="",
            # 新增：存储 ASR 情感
            asr_emotion=asr_emotion,
            input_type="分析中"
        )

        logger.info(f"✅ 记录创建成功，ID: {record.id}，启动后台分析任务")

        # 4. 后台异步执行情绪分析
        async def analyze_and_update():
            """后台任务：分析情绪并更新记录"""
            try:
                from app.database import SessionLocal
                db_bg = SessionLocal()

                t2 = time.time()
                analysis = await ai_service.analyze_record(transcribed_text)
                t3 = time.time()
                logger.info(f"⏱️ [后台] 情绪分析耗时: {t3-t2:.2f}秒")

                # 更新记录
                record_service.update_record_analysis(
                    db=db_bg,
                    record_id=record.id,
                    emotion=analysis.get("emotion", "neutral"),
                    emotion_score=analysis.get("emotion_score", 0.5),
                    keywords=analysis.get("keywords", []),
                    topics=analysis.get("topics", []),
                    mixed_emotions=analysis.get("mixed_emotions"),
                    primary_emotion=analysis.get("primary_emotion", "平静"),
                    triggers=analysis.get("triggers"),
                    unspoken_need=analysis.get("unspoken_need", ""),
                    energy_level=analysis.get("energy_level", 5),
                    brief_summary=analysis.get("brief_summary", ""),
                    # 新增
                    input_type=analysis.get("input_type", "情绪表达")
                )
                logger.info(f"✅ [后台] 记录分析更新完成，ID: {record.id}")
                db_bg.close()
            except Exception as e:
                logger.error(f"❌ [后台] 分析任务失败: {e}")

        background_tasks.add_task(analyze_and_update)

        return ApiResponse(
            data=RecordResponse.model_validate(record),
            message="记录成功"
        )

    except Exception as e:
        logger.error(f"创建语音记录失败: {e}")
        return ApiResponse(
            success=False,
            data=None,
            message=f"记录失败: {str(e)}"
        )
