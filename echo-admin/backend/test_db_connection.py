#!/usr/bin/env python3
"""
数据库连接测试脚本
用法: python test_db_connection.py
"""

import sys
from sqlalchemy import text
from app.config import settings
from app.database import engine


def test_connection():
    """测试数据库连接"""

    print("=" * 50)
    print("数据库连接测试")
    print("=" * 50)

    # 显示当前配置
    print("\n【当前配置】")
    print(f"  主机: {settings.DB_HOST}")
    print(f"  端口: {settings.DB_PORT}")
    print(f"  用户: {settings.DB_USER}")
    print(f"  数据库: {settings.DB_NAME}")
    print(f"  连接URL: mysql+pymysql://{settings.DB_USER}:***@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    print("\n【测试连接】...")

    try:
        # 测试连接
        with engine.connect() as conn:
            # 执行简单查询
            result = conn.execute(text("SELECT VERSION()"))
            version = result.scalar()

            # 查询数据库列表
            result = conn.execute(text("SHOW DATABASES"))
            databases = [row[0] for row in result]

            print(f"  ✅ 连接成功！")
            print(f"  MySQL 版本: {version}")

            # 检查目标数据库是否存在
            if settings.DB_NAME in databases:
                print(f"  ✅ 数据库 '{settings.DB_NAME}' 存在")

                # 查询该数据库的表
                result = conn.execute(text(f"SHOW TABLES FROM {settings.DB_NAME}"))
                tables = [row[0] for row in result]
                if tables:
                    print(f"  📋 数据表 ({len(tables)}): {', '.join(tables)}")
                else:
                    print(f"  ⚠️  数据库 '{settings.DB_NAME}' 为空，没有表")
            else:
                print(f"  ❌ 数据库 '{settings.DB_NAME}' 不存在")
                print(f"  可用数据库: {', '.join(databases)}")
                return 1

        print("\n" + "=" * 50)
        print("测试通过！数据库配置正确。")
        print("=" * 50)
        return 0

    except Exception as e:
        print(f"\n  ❌ 连接失败！")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {e}")

        # 给出排查建议
        print("\n【排查建议】")
        if "Can't connect" in str(e) or "Connection refused" in str(e):
            print("  1. 检查 MySQL 服务是否启动")
            print("  2. 检查 DB_HOST 和 DB_PORT 是否正确")
        elif "Access denied" in str(e):
            print("  1. 检查 DB_USER 和 DB_PASSWORD 是否正确")
            print("  2. 确认用户有权限访问该数据库")
        elif "Unknown database" in str(e):
            print(f"  1. 创建数据库: CREATE DATABASE {settings.DB_NAME};")
        elif "No module named 'pymysql'" in str(e):
            print("  1. 安装依赖: pip install pymysql")

        print("\n" + "=" * 50)
        return 1


if __name__ == "__main__":
    sys.exit(test_connection())
