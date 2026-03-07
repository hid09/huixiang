"""
性能测试
测试目标：验证核心函数和 API 的响应时间
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import time

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.main import app
from app.services.diary_service import _is_valid_record, _calc_info_score
from app.services.record_service import get_diary_date


# ==================== 测试数据库配置 ====================

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ==================== Fixtures ====================

@pytest.fixture(scope="module")
def client():
    """创建测试客户端"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_token(client):
    """获取认证 Token"""
    # 注册用户
    client.post("/api/user/register", json={
        "username": "perf_user",
        "password": "Test123456!",
        "name": "性能测试用户"
    })
    # 登录
    response = client.post("/api/user/login", json={
        "username": "perf_user",
        "password": "Test123456!"
    })
    return response.json()["data"]["access_token"]


# ==================== 函数性能测试 ====================

class TestFunctionPerformance:
    """函数性能测试"""

    def test_noise_filter_performance(self, benchmark):
        """测试噪音过滤函数性能"""
        test_texts = [
            "今天完成了一个重要功能开发",
            "嗯嗯啊啊",
            "Hello",
            "这是一个正常的测试文本，包含了一些内容",
            "产品开发还是要遵循定好的规则",
        ] * 20  # 100 个测试样本

        def filter_all():
            return [_is_valid_record(text) for text in test_texts]

        result = benchmark(filter_all)
        assert len(result) == 100

    def test_info_score_performance(self, benchmark):
        """测试信息量评分函数性能"""
        test_texts = [
            "今天好累啊，但是很有成就感",
            "完成了一个重要的项目",
            "测试",
            "这是一个比较长的测试文本，包含了很多信息量，用于测试评分函数的性能",
        ] * 25  # 100 个测试样本

        def score_all():
            return [_calc_info_score(text) for text in test_texts]

        result = benchmark(score_all)
        assert len(result) == 100

    def test_diary_date_performance(self, benchmark):
        """测试跨天日期函数性能"""
        # get_diary_date() 无参数，使用当前时间
        # 测试连续调用 100 次的性能
        def date_all():
            return [get_diary_date() for _ in range(100)]

        result = benchmark(date_all)
        assert len(result) == 100


# ==================== API 响应时间测试 ====================

class TestAPIResponseTime:
    """API 响应时间测试"""

    def test_register_response_time(self, benchmark, client):
        """测试注册接口响应时间"""
        def register():
            return client.post("/api/user/register", json={
                "username": f"perf_user_{time.time_ns()}",
                "password": "Test123456!",
                "name": "性能测试"
            })

        response = benchmark(register)
        assert response.status_code == 200

    def test_login_response_time(self, benchmark, client):
        """测试登录接口响应时间"""
        # 先注册
        client.post("/api/user/register", json={
            "username": "login_perf_user",
            "password": "Test123456!",
            "name": "登录性能测试"
        })

        def login():
            return client.post("/api/user/login", json={
                "username": "login_perf_user",
                "password": "Test123456!"
            })

        response = benchmark(login)
        assert response.status_code == 200

    def test_create_record_response_time(self, benchmark, client, auth_token):
        """测试创建记录接口响应时间"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        def create_record():
            return client.post("/api/records/text", headers=headers, json={
                "text": "这是一条性能测试记录"
            })

        response = benchmark(create_record)
        assert response.status_code == 200

    def test_get_records_list_response_time(self, benchmark, client, auth_token):
        """测试获取记录列表响应时间"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        # 先创建一些记录
        for i in range(10):
            client.post("/api/records/text", headers=headers, json={
                "text": f"测试记录 {i}"
            })

        def get_records():
            return client.get("/api/records", headers=headers)

        response = benchmark(get_records)
        assert response.status_code == 200

    def test_get_diary_list_response_time(self, benchmark, client, auth_token):
        """测试获取日记列表响应时间"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        def get_diaries():
            return client.get("/api/diaries", headers=headers)

        response = benchmark(get_diaries)
        assert response.status_code == 200


# ==================== 性能基准 ====================

class TestPerformanceBenchmarks:
    """性能基准测试"""

    def test_noise_filter_baseline(self, benchmark):
        """噪音过滤基准：1000 次调用 < 100ms"""
        test_text = "今天完成了一个重要功能开发，感觉很有成就感"

        result = benchmark(lambda: [_is_valid_record(test_text) for _ in range(1000)])
        assert len(result) == 1000
        # 平均每次调用 < 0.1ms
        assert benchmark.stats['mean'] < 0.0001

    def test_api_response_baseline(self, benchmark, client, auth_token):
        """API 响应基准：P95 < 200ms"""
        headers = {"Authorization": f"Bearer {auth_token}"}

        response = benchmark(lambda: client.get("/api/records/today", headers=headers))
        assert response.status_code == 200
        # 平均响应时间 < 0.2s
        assert benchmark.stats['mean'] < 0.2
