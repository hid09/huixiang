#!/usr/bin/env python3
"""
初始化脚本：创建默认管理员账号
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import AdminUser
from app.utils.password import get_password_hash


def create_default_admin():
    """创建默认管理员账号"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # 检查是否已存在管理员
        existing = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if existing:
            print(f"管理员 'admin' 已存在，跳过创建")
            return

        # 创建默认管理员
        admin = AdminUser(
            username="admin",
            password_hash=get_password_hash("admin123"),
            role="super",
        )
        db.add(admin)
        db.commit()

        print("=" * 50)
        print("默认管理员账号创建成功！")
        print("=" * 50)
        print(f"用户名: admin")
        print(f"密码: admin123")
        print(f"角色: super (超级管理员)")
        print("=" * 50)
        print("⚠️  请及时修改默认密码！")
        print("=" * 50)

    except Exception as e:
        print(f"创建失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_default_admin()
