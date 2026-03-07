"""
用户服务
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.auth import hash_password


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
