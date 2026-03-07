"""
用户服务
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserUpdate, UserStatsResponse
from app.core.auth import hash_password
from datetime import datetime


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """根据ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()


def create_user_with_password(db: Session, username: str, password: str, name: str = "回响用户") -> User:
    """创建带密码的用户"""
    user = User(
        username=username,
        password_hash=hash_password(password),
        name=name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_user(db: Session, device_id: str, name: str = "回响用户") -> User:
    """
    根据设备ID获取或创建用户（单人版）
    """
    user = db.query(User).filter(User.device_id == device_id).first()
    if user:
        return user

    # 创建新用户
    user = User(
        device_id=device_id,
        name=name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_device_id(db: Session, device_id: str) -> Optional[User]:
    """根据设备ID获取用户"""
    return db.query(User).filter(User.device_id == device_id).first()


def update_user(db: Session, device_id: str, update: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    user = get_user_by_device_id(db, device_id)
    if not user:
        return None

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def get_user_stats(db: Session, device_id: str) -> UserStatsResponse:
    """获取用户统计数据"""
    user = get_user_by_device_id(db, device_id)
    if not user:
        return UserStatsResponse(
            total_record_days=0,
            total_voice_count=0,
            continuous_days=0,
            longest_continuous_days=0,
            this_month_days=0,
            this_month_percentage=0.0
        )

    # 计算本月记录天数
    from app.services.record_service import get_month_record_days
    this_month_days = get_month_record_days(db, device_id)

    # 计算本月占比
    today = datetime.now()
    days_in_month = today.day
    this_month_percentage = round(this_month_days / days_in_month * 100, 1) if days_in_month > 0 else 0

    return UserStatsResponse(
        total_record_days=user.total_record_days,
        total_voice_count=user.total_voice_count,
        continuous_days=user.continuous_days,
        longest_continuous_days=user.longest_continuous_days,
        this_month_days=this_month_days,
        this_month_percentage=this_month_percentage
    )
