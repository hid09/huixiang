"""
认证模块测试
测试登录、退出、获取当前用户信息

注意：这些测试需要后端服务运行，并且数据库中有测试数据
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.security import create_access_token, decode_access_token


@pytest.mark.auth
class TestJWTSecurity:
    """JWT 安全测试（不需要数据库）"""

    def test_create_token_valid(self):
        """测试创建有效token"""
        data = {
            "sub": "1",
            "username": "admin",
            "role": "super"
        }
        token = create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT token 通常较长

    def test_decode_token_valid(self):
        """测试解码有效token"""
        data = {
            "sub": "1",
            "username": "admin",
            "role": "super"
        }
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["username"] == "admin"
        assert payload["role"] == "super"

    @pytest.mark.security
    def test_decode_invalid_token(self):
        """测试解码无效token"""
        invalid_tokens = [
            "",  # 空token
            "invalid.token.here",  # 格式错误
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.wrong",  # 错误签名
            "not-even-a-jwt",  # 完全无效
        ]
        for token in invalid_tokens:
            payload = decode_access_token(token)
            assert payload is None, f"应该拒绝无效token: {token}"

    @pytest.mark.security
    def test_none_algorithm_attack(self):
        """测试 none 算法攻击"""
        # 尝试使用 none 算法绕过签名验证
        none_token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJzdXBlciJ9."
        payload = decode_access_token(none_token)
        # 应该被拒绝（算法不匹配）
        assert payload is None

    def test_token_has_expiration(self):
        """测试token包含过期时间"""
        data = {"sub": "1", "username": "admin"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload is not None
        assert "exp" in payload
        # exp 应该是未来时间戳
        import time
        assert payload["exp"] > int(time.time())


@pytest.mark.auth
@pytest.mark.security
class TestAuthenticationSecurity:
    """认证安全测试（需要运行的服务）"""

    async def test_missing_token_returns_401(self):
        """测试缺少token返回401/403"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/admin/me")
            # HTTPBearer 可能返回 401 或 403
            assert response.status_code in [401, 403]

    async def test_malformed_token_returns_401(self):
        """测试格式错误的token返回401"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/admin/me",
                headers={"Authorization": "Bearer not-a-valid-jwt"}
            )
            assert response.status_code == 401

    async def test_invalid_scheme_returns_401(self):
        """测试错误的认证方案"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # 使用错误的scheme（不是Bearer）
            response = await client.get(
                "/api/admin/me",
                headers={"Authorization": f"Basic {create_access_token({'sub': '1'})}"}
            )
            # HTTPBearer 要求 Bearer scheme，可能返回 401 或 403
            assert response.status_code in [401, 403]

    async def test_tampered_token_returns_401(self):
        """测试被篡改的token"""
        valid_token = create_access_token({"sub": "1", "username": "admin"})
        # 篡改token（修改部分字符）
        tampered_token = valid_token[:-5] + "wrong"
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/admin/me",
                headers={"Authorization": f"Bearer {tampered_token}"}
            )
            assert response.status_code == 401


@pytest.mark.auth
class TestLoginAPI:
    """登录API测试（需要数据库）"""

    async def test_login_missing_fields(self):
        """测试缺少字段"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # 缺少password
            response = await client.post(
                "/api/admin/login",
                json={"username": "admin"}
            )
            assert response.status_code == 422  # ValidationError

    async def test_login_empty_fields(self):
        """测试空字段"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/admin/login",
                json={"username": "", "password": ""}
            )
            # 应该返回验证错误或认证失败
            assert response.status_code in [200, 422]

    @pytest.mark.security
    @pytest.mark.skip(reason="需要数据库连接")
    async def test_sql_injection_in_username(self):
        """SQL注入测试：用户名字段"""
        injection_payloads = [
            "admin' OR '1'='1",
            "admin'--",
            "admin'/*",
            "' OR '1'='1'--",
            "admin' UNION SELECT * FROM users--",
            "'; DROP TABLE admin_users--",
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for payload in injection_payloads:
                response = await client.post(
                    "/api/admin/login",
                    json={
                        "username": payload,
                        "password": "anypassword"
                    }
                )
                # 所有注入尝试都应该失败
                # 可能返回200但code=401，或者直接返回401
                if response.status_code == 200:
                    data = response.json()
                    assert data.get("code") == 401, f"SQL注入可能成功: {payload}"


@pytest.mark.auth
class TestLogoutAPI:
    """退出API测试"""

    async def test_logout_always_succeeds(self):
        """测试退出总是成功（无状态JWT）"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # 无token也可以调用logout（前端删除token即可）
            response = await client.post("/api/admin/logout")
            assert response.status_code == 200
            data = response.json()
            assert data.get("code") == 200
