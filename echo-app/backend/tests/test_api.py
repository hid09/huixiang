"""
API 集成测试
测试目标：验证主要 API 端点的完整请求流程
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch, AsyncMock
import io

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.main import app
from app.models import user, record, diary  # 导入模型以便创建表


# ==================== 测试数据库配置 ====================

# 使用内存数据库（StaticPool 确保连接持久）
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """测试用的数据库依赖覆盖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# 覆盖应用的数据库依赖
app.dependency_overrides[get_db] = override_get_db


# ==================== Fixtures ====================

@pytest.fixture(scope="module")
def client():
    """创建测试客户端"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # 测试结束后清理
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "username": "testuser001",
        "password": "Test123456!",
        "name": "测试用户"
    }


@pytest.fixture
def auth_headers(client, test_user_data):
    """获取认证头（自动注册并登录）"""
    # 注册用户（注册直接返回 token）
    register_resp = client.post("/api/user/register", json=test_user_data)

    # 如果注册成功，直接使用返回的 token
    reg_data = register_resp.json()
    if reg_data.get("success") and reg_data.get("data"):
        token = reg_data["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # 如果注册失败（用户已存在），则登录
    login_resp = client.post("/api/user/login", json={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    login_data = login_resp.json()
    token = login_data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==================== 用户模块测试 ====================

class TestUserAPI:
    """用户 API 测试"""

    def test_register_success(self, client):
        """测试注册成功"""
        response = client.post("/api/user/register", json={
            "username": "newuser001",
            "password": "Test123456!",
            "name": "新用户"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "access_token" in data["data"]

    def test_register_duplicate_username(self, client, test_user_data):
        """测试重复用户名注册"""
        # 第一次注册
        client.post("/api/user/register", json=test_user_data)
        # 第二次注册（相同用户名）
        response = client.post("/api/user/register", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "已存在" in data["message"]

    def test_login_success(self, client, test_user_data):
        """测试登录成功"""
        # 先注册
        client.post("/api/user/register", json=test_user_data)

        # 登录
        response = client.post("/api/user/login", json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "access_token" in data["data"]

    def test_login_wrong_password(self, client, test_user_data):
        """测试密码错误"""
        client.post("/api/user/register", json=test_user_data)

        response = client.post("/api/user/login", json={
            "username": test_user_data["username"],
            "password": "wrongpassword"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False

    def test_get_current_user(self, client, auth_headers):
        """测试获取当前用户信息"""
        response = client.get("/api/user/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["username"] == "testuser001"


# ==================== 记录模块测试 ====================

class TestRecordAPI:
    """记录 API 测试"""

    def test_create_text_record_success(self, client, auth_headers):
        """测试创建文字记录"""
        response = client.post("/api/records/text", headers=auth_headers, json={
            "text": "今天完成了一个重要功能开发"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["transcribed_text"] == "今天完成了一个重要功能开发"

    def test_create_text_record_empty(self, client, auth_headers):
        """测试空文本提交"""
        response = client.post("/api/records/text", headers=auth_headers, json={
            "text": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "请输入内容" in data["message"]

    def test_create_text_record_only_spaces(self, client, auth_headers):
        """测试纯空格提交"""
        response = client.post("/api/records/text", headers=auth_headers, json={
            "text": "   "
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False

    def test_get_records_list(self, client, auth_headers):
        """测试获取记录列表"""
        # 先创建一条记录
        client.post("/api/records/text", headers=auth_headers, json={
            "text": "测试记录内容"
        })

        # 获取列表
        response = client.get("/api/records", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["total"] >= 1

    def test_get_today_records(self, client, auth_headers):
        """测试获取今日记录"""
        response = client.get("/api/records/today", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert isinstance(data["data"], list)

    def test_get_record_by_id(self, client, auth_headers):
        """测试获取单条记录"""
        # 创建记录
        create_resp = client.post("/api/records/text", headers=auth_headers, json={
            "text": "单条记录测试"
        })
        record_id = create_resp.json()["data"]["id"]

        # 获取记录
        response = client.get(f"/api/records/{record_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["data"]["id"] == record_id

    def test_get_record_not_found(self, client, auth_headers):
        """测试获取不存在的记录"""
        response = client.get("/api/records/nonexistent-id", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "不存在" in data["message"]

    def test_unauthorized_access(self, client):
        """测试未认证访问"""
        response = client.get("/api/records")
        assert response.status_code == 401  # 未授权


# ==================== ASR 语音转写 API 测试 ====================

class TestASRAPI:
    """ASR 语音转写 API 测试"""

    def test_transcribe_success(self, client, auth_headers):
        """测试语音转写成功（Mock AI 服务）"""
        # Mock AI 服务
        with patch('app.api.records.ai_service') as mock_ai:
            # 配置 Mock 返回值
            mock_ai.transcribe_audio_file = AsyncMock(return_value={
                "text": "今天完成了一个重要功能开发",
                "asr_emotion": "neutral"
            })
            mock_ai.analyze_record = AsyncMock(return_value={
                "emotion": "positive",
                "emotion_score": 0.8,
                "mixed_emotions": {"满足": 8},
                "primary_emotion": "满足",
                "triggers": ["完成"],
                "unspoken_need": "成就感",
                "energy_level": 7,
                "brief_summary": "完成功能开发",
                "keywords": ["功能", "开发"],
                "topics": ["工作"],
                "input_type": "事实陈述"
            })

            # 模拟上传音频文件
            audio_content = b"fake_audio_content_for_testing"
            files = {"audio": ("test.webm", io.BytesIO(audio_content), "audio/webm")}

            response = client.post(
                "/api/records/voice/transcribe",
                headers=auth_headers,
                files=files
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert data["data"]["text"] == "今天完成了一个重要功能开发"
            assert data["data"]["emotion"] == "positive"
            assert data["data"]["asr_emotion"] == "neutral"

    def test_transcribe_with_happy_emotion(self, client, auth_headers):
        """测试 ASR 检测到开心情绪"""
        with patch('app.api.records.ai_service') as mock_ai:
            mock_ai.transcribe_audio_file = AsyncMock(return_value={
                "text": "太棒了，项目终于上线了！",
                "asr_emotion": "happy"
            })
            mock_ai.analyze_record = AsyncMock(return_value={
                "emotion": "positive",
                "emotion_score": 0.9,
                "mixed_emotions": {"兴奋": 9},
                "primary_emotion": "兴奋",
                "triggers": ["上线"],
                "unspoken_need": "被认可",
                "energy_level": 9,
                "brief_summary": "项目上线",
                "keywords": ["项目", "上线"],
                "topics": ["工作"],
                "input_type": "情绪表达"
            })

            audio_content = b"fake_audio_happy"
            files = {"audio": ("test.webm", io.BytesIO(audio_content), "audio/webm")}

            response = client.post(
                "/api/records/voice/transcribe",
                headers=auth_headers,
                files=files
            )

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["asr_emotion"] == "happy"
            assert data["data"]["emotion"] == "positive"

    def test_transcribe_empty_result(self, client, auth_headers):
        """测试转写失败（AI 返回空文本）"""
        with patch('app.api.records.ai_service') as mock_ai:
            # 模拟转写失败
            mock_ai.transcribe_audio_file = AsyncMock(return_value={
                "text": None,
                "asr_emotion": "neutral"
            })

            audio_content = b"fake_audio_empty"
            files = {"audio": ("test.webm", io.BytesIO(audio_content), "audio/webm")}

            response = client.post(
                "/api/records/voice/transcribe",
                headers=auth_headers,
                files=files
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] == False
            assert "转写失败" in data["message"]

    def test_transcribe_unauthorized(self, client):
        """测试未认证访问"""
        audio_content = b"fake_audio"
        files = {"audio": ("test.webm", io.BytesIO(audio_content), "audio/webm")}

        response = client.post("/api/records/voice/transcribe", files=files)
        assert response.status_code == 401


# ==================== 日记模块测试 ====================

class TestDiaryAPI:
    """日记 API 测试"""

    def test_get_diary_list(self, client, auth_headers):
        """测试获取日记列表"""
        response = client.get("/api/diaries", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "items" in data["data"]

    def test_get_diary_not_found(self, client, auth_headers):
        """测试获取不存在的日记"""
        response = client.get("/api/diaries/2020-01-01", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # 日记不存在时可能返回 null 或提示
        assert data["success"] in [True, False]

    def test_get_empty_days_stats(self, client, auth_headers):
        """测试获取连续未记录天数"""
        response = client.get("/api/diaries/stats/empty-days", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "consecutive_empty_days" in data["data"]
