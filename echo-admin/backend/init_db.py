#!/usr/bin/env python3
"""
数据库初始化脚本：创建所有表和默认管理员账号
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base
from app.models import AdminUser
from app.utils.password import get_password_hash


def init_database():
    """初始化数据库"""
    print(f"使用数据库: {settings.DATABASE_URL}")

    # 创建引擎
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if settings.USE_SQLITE else {}
    )

    # 创建所有表
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")

    # 创建会话
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
    init_database()
