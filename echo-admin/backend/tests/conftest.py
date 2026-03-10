"""
pytest 配置文件
提供测试fixtures和通用配置
"""
import pytest
from typing import AsyncGenerator
from unittest.mock import Mock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.security import create_access_token
from app.models import AdminUser, User


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端（不需要数据库）"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def super_user_token() -> str:
    """生成超级管理员token（用于需要认证的测试）"""
    data = {
        "sub": "1",
        "username": "admin",
        "role": "super"
    }
    return create_access_token(data)


@pytest.fixture
def viewer_user_token() -> str:
    """生成普通管理员token（用于权限测试）"""
    data = {
        "sub": "2",
        "username": "viewer",
        "role": "viewer"
    }
    return create_access_token(data)


@pytest.fixture
def super_auth_headers(super_user_token: str) -> dict:
    """超级管理员认证headers"""
    return {"Authorization": f"Bearer {super_user_token}"}


@pytest.fixture
def viewer_auth_headers(viewer_user_token: str) -> dict:
    """普通管理员认证headers"""
    return {"Authorization": f"Bearer {viewer_user_token}"}


@pytest.fixture
def mock_super_admin():
    """Mock 超级管理员对象"""
    admin = Mock(spec=AdminUser)
    admin.id = 1
    admin.username = "admin"
    admin.role = "super"
    admin.created_at = "2026-01-01T10:00:00"
    return admin


@pytest.fixture
def mock_viewer_admin():
    """Mock 普通管理员对象"""
    admin = Mock(spec=AdminUser)
    admin.id = 2
    admin.username = "viewer"
    admin.role = "viewer"
    admin.created_at = "2026-01-02T10:00:00"
    return admin


@pytest.fixture
def mock_user():
    """Mock 用户对象"""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser001"
    user.phone = "13800138000"
    user.created_at = "2026-01-01T10:00:00"
    return user


# ===== Mock 数据 Fixtures =====

@pytest.fixture
def mock_admin_user_data():
    """Mock管理员数据"""
    return {
        "username": "testadmin",
        "password": "testpass123",
        "role": "viewer"
    }


@pytest.fixture
def mock_login_data():
    """Mock登录数据"""
    return {
        "username": "admin",
        "password": "admin123"
    }


@pytest.fixture
def mock_user_data():
    """Mock用户数据"""
    return {
        "id": 1,
        "username": "testuser",
        "phone": "13800138000",
        "created_at": "2026-01-01T10:00:00",
        "records_count": 150,
        "diaries_count": 45,
        "last_active": "2026-03-09T15:30:00"
    }


@pytest.fixture
def mock_record_data():
    """Mock录音记录数据"""
    return {
        "id": 1001,
        "user_id": 1,
        "content": "今天天气真不错",
        "created_at": "2026-03-09T15:30:00",
        "emotion_type": "positive",
        "asr_emotion": "happy",
        "mood_tag": "开心",
        "input_type": "情绪表达"
    }


@pytest.fixture
def mock_diary_data():
    """Mock日记数据"""
    return {
        "id": 201,
        "user_id": 1,
        "diary_date": "2026-03-09",
        "emotion_type": "positive",
        "mood_tag": "平静",
        "keywords": ["天气", "散步", "咖啡"],
        "what_happened": "今天天气不错，出去散步了",
        "thoughts": "感觉心情放松了很多",
        "small_discovery": "公园的樱花开了",
        "records_count": 3
    }


@pytest.fixture
def mock_dashboard_stats():
    """Mock看板统计数据"""
    return {
        "overview": {
            "total_users": 1234,
            "dau_today": 56,
            "records_today": 128,
            "diaries_today": 45
        },
        "ai_health": {
            "success_count": 48,
            "fail_count": 2,
            "fail_rate": 4.0
        },
        "trend_7d": {
            "dates": ["03-03", "03-04", "03-05", "03-06", "03-07", "03-08", "03-09"],
            "new_users": [12, 8, 15, 10, 6, 14, 9],
            "active_users": [45, 52, 48, 60, 55, 58, 56],
            "records": [89, 102, 95, 120, 108, 115, 128],
            "diaries": [34, 40, 38, 45, 42, 44, 45]
        }
    }
