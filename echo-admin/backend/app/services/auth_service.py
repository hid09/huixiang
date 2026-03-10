from typing import Optional
from sqlalchemy.orm import Session

from app.models import AdminUser
from app.utils.password import verify_password
from app.security import create_access_token


class AuthService:
    """认证服务"""

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[AdminUser]:
        """验证管理员登录"""
        admin = db.query(AdminUser).filter(AdminUser.username == username).first()
        if not admin:
            return None
        if not verify_password(password, admin.password_hash):
            return None
        return admin

    @staticmethod
    def create_token(admin: AdminUser) -> str:
        """创建访问令牌"""
        data = {"sub": str(admin.id), "username": admin.username, "role": admin.role}
        return create_access_token(data)
