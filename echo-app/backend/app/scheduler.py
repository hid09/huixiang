"""
定时任务调度器
- 每天早上 6:00 自动生成日记
"""
import logging
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services import diary_service, record_service

logger = logging.getLogger(__name__)

# 中国时区
CHINA_TZ = timezone(timedelta(hours=8))

# 创建调度器
scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


async def generate_daily_diary_job():
    """
    定时任务：为所有有记录但未生成日记的用户生成日记

    每天早上 6:00 执行
    """
    logger.info("⏰ 开始执行日记生成任务...")

    db: Session = SessionLocal()
    try:
        # 获取昨天的日期（中国时区，因为每天6点生成的是前一天的日记）
        yesterday = (datetime.now(CHINA_TZ) - timedelta(days=1)).strftime("%Y-%m-%d")

        # 获取昨天有记录的所有用户
        users_with_records = record_service.get_users_with_records_on_date(db, yesterday)

        if not users_with_records:
            logger.info(f"昨天 ({yesterday}) 没有任何记录")
            return

        logger.info(f"昨天 ({yesterday}) 有 {len(users_with_records)} 个用户有记录")

        success_count = 0
        for user_id in users_with_records:
            try:
                # 检查是否已有日记
                existing = diary_service.get_diary_by_date(db, user_id, yesterday)
                if existing:
                    logger.info(f"用户 {user_id} 的日记已存在，跳过")
                    continue

                # 生成日记
                diary = await diary_service.generate_diary(db, user_id, yesterday)
                if diary:
                    success_count += 1
                    logger.info(f"✅ 用户 {user_id} 的日记生成成功")
                else:
                    logger.warning(f"⚠️ 用户 {user_id} 的日记生成失败")

            except Exception as e:
                logger.error(f"❌ 用户 {user_id} 日记生成异常: {e}")

        logger.info(f"🎉 日记生成任务完成：成功 {success_count}/{len(users_with_records)}")

    except Exception as e:
        logger.error(f"❌ 日记生成任务异常: {e}")
    finally:
        db.close()


def setup_scheduler():
    """设置定时任务"""
    # 每天早上 6:00 执行
    scheduler.add_job(
        generate_daily_diary_job,
        CronTrigger(hour=6, minute=0, timezone="Asia/Shanghai"),
        id="generate_daily_diary",
        name="每日日记生成",
        replace_existing=True
    )

    logger.info("✅ 定时任务已设置：每天 06:00 生成日记")


def start_scheduler():
    """启动调度器"""
    setup_scheduler()
    scheduler.start()
    logger.info("🚀 定时任务调度器已启动")


def shutdown_scheduler():
    """关闭调度器"""
    scheduler.shutdown()
    logger.info("⏹️ 定时任务调度器已关闭")
