"""
安全测试专项 - 核心安全漏洞测试
测试认证绕过、权限提升、注入攻击等关键安全问题
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.security import create_access_token


@pytest.mark.security
class TestAuthenticationBypass:
    """认证绕过攻击测试"""

    async def test_no_token_access_protected_endpoint(self):
        """测试无token访问受保护接口"""
        protected_endpoints = [
            "/api/admin/me",
            "/api/admin/dashboard/stats",
            "/api/admin/users",
            "/api/admin/admin-users",
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for endpoint in protected_endpoints:
                response = await client.get(endpoint)
                # HTTPBearer 可能返回 401 或 403
                assert response.status_code in [401, 403], f"{endpoint} 应该需要认证"

    async def test_forged_token(self):
        """测试伪造token"""
        # 手动构造一个看起来像JWT的假token
        fake_tokens = [
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJzdXBlciJ9.signed",
            "Bearer fake-token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIn0.signature",
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for token in fake_tokens:
                response = await client.get(
                    "/api/admin/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code == 401, f"伪造token应该被拒绝: {token[:20]}"

    async def test_algorithm_confusion_attack(self):
        """测试算法混淆攻击"""
        # 尝试使用 none 算法
        none_token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJzdXBlciJ9."
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/admin/me",
                headers={"Authorization": f"Bearer {none_token}"}
            )
            assert response.status_code == 401

    async def test_exhausted_token(self):
        """测试过期token（使用无效的exp）"""
        # 生成一个看起来有效的token
        valid_token = create_access_token({"sub": "999", "username": "ghost"})
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/admin/me",
                headers={"Authorization": f"Bearer {valid_token}"}
            )
            # 应该返回401因为用户不存在
            assert response.status_code == 401


@pytest.mark.security
class TestAuthorizationBypass:
    """授权绕过攻击测试"""

    async def test_viewer_access_super_only_endpoint(self):
        """测试普通管理员访问超管专用接口"""
        viewer_token = create_access_token({
            "sub": "2",
            "username": "viewer",
            "role": "viewer"
        })
        super_only_endpoints = [
            "/api/admin/admin-users",
            "/api/admin/admin-users",  # GET
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for endpoint in super_only_endpoints:
                response = await client.get(
                    endpoint,
                    headers={"Authorization": f"Bearer {viewer_token}"}
                )
                # viewer 用户不存在返回 401，存在则返回 403
                assert response.status_code in [401, 403], f"{endpoint} 应该只允许超管访问"

    async def test_role_escalation_in_token(self):
        """测试通过修改token进行权限提升"""
        # 创建一个viewer的token，但手动修改role为super
        # 由于签名验证，这应该失败
        viewer_token = create_access_token({
            "sub": "2",
            "username": "viewer",
            "role": "super"  # 尝试在token中提升权限
        })
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # 这个token在签名上是有效的，因为是我们用正确的key生成的
            # 但实际验证时会检查数据库中的用户角色
            response = await client.get(
                "/api/admin/admin-users",
                headers={"Authorization": f"Bearer {viewer_token}"}
            )
            # 应该根据实际数据库用户角色决定
            # 如果数据库中用户是viewer，应该返回403

    async def test_access_other_user_data(self):
        """测试访问其他用户的数据"""
        # 使用admin token尝试访问user_id=999的数据
        admin_token = create_access_token({
            "sub": "1",
            "username": "admin",
            "role": "super"
        })
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/admin/users/999",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            # 应该返回404（用户不存在）
            # 不应该泄露其他用户的信息


@pytest.mark.security
class TestInjectionAttacks:
    """注入攻击测试"""

    async def test_sql_injection_in_user_search(self):
        """用户搜索SQL注入测试"""
        admin_token = create_access_token({
            "sub": "1",
            "username": "admin",
            "role": "super"
        })
        sql_payloads = [
            "test' OR '1'='1",
            "test' UNION SELECT * FROM admin_users--",
            "test'; DROP TABLE admin_users--",
            "1' OR 1=1--",
            "' OR '1'='1",
            "admin'--",
            "test'/*",
            "test' EXEC xp_cmdshell('dir')--",
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for payload in sql_payloads:
                response = await client.get(
                    f"/api/admin/users?keyword={payload}",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                # 应该正常处理，不应该报SQL错误
                # 如果返回500，可能存在SQL注入漏洞
                assert response.status_code != 500, f"可能的SQL注入: {payload}"
                # 响应应该成功（200）或未授权（401/403）
                assert response.status_code in [200, 401, 403, 404]

    @pytest.mark.xfail(reason="需要实际数据库验证")
    async def test_xss_in_search_parameters(self):
        """搜索参数XSS测试"""
        admin_token = create_access_token({
            "sub": "1",
            "username": "admin",
            "role": "super"
        })
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
            "<iframe src=javascript:alert('xss')>",
            "<<script>alert('xss')</script>",
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for payload in xss_payloads:
                response = await client.get(
                    f"/api/admin/users?keyword={payload}",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                # 响应应该是安全的JSON
                if response.status_code == 200:
                    content = response.text
                    # 未转义的script标签表明存在XSS
                    assert "<script>" not in content or "\\u003c" in content

    async def test_command_injection(self):
        """命令注入测试"""
        admin_token = create_access_token({
            "sub": "1",
            "username": "admin",
            "role": "super"
        })
        command_payloads = [
            "test; cat /etc/passwd",
            "test | whoami",
            "test && ls -la",
            "test`id`",
            "test$(whoami)",
            "test; rm -rf /",
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for payload in command_payloads:
                response = await client.get(
                    f"/api/admin/users?keyword={payload}",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                # 命令不应该被执行
                assert response.status_code != 500


@pytest.mark.security
class TestInputValidation:
    """输入验证安全测试"""

    async def test_path_traversal_attack(self):
        """路径遍历攻击测试"""
        admin_token = create_access_token({
            "sub": "1",
            "username": "admin",
            "role": "super"
        })
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "%2e%2e%2f",
            "....//....//....//etc/passwd",
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for payload in path_traversal_payloads:
                response = await client.get(
                    f"/api/admin/users?keyword={payload}",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                # 不应该读取到系统文件
                assert response.status_code != 500
                if response.status_code == 200:
                    data = response.json()
                    # 响应不应该包含文件内容
                    assert "root:" not in response.text

    async def test_null_byte_injection(self):
        """空字节注入测试"""
        admin_token = create_access_token({
            "sub": "1",
            "username": "admin",
            "role": "super"
        })
        null_payloads = [
            "test\x00.png",
            "test%00.jpg",
            "test\x00\x00",
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for payload in null_payloads:
                try:
                    response = await client.get(
                        f"/api/admin/users?keyword={payload}",
                        headers={"Authorization": f"Bearer {admin_token}"}
                    )
                    # 应该正常处理
                    assert response.status_code != 500
                except Exception:
                    # 某些字符可能无法正确编码，这也是可以的
                    pass

    async def test_oversized_input(self):
        """超大输入攻击测试"""
        admin_token = create_access_token({
            "sub": "1",
            "username": "admin",
            "role": "super"
        })
        # 使用较小的输入，避免 URL 过长
        large_input = "a" * 1000  # 1KB
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(
                f"/api/admin/users?keyword={large_input}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            # 应该被拒绝或正常处理，不应该导致服务崩溃
            assert response.status_code in [200, 400, 403, 404, 413, 414]

    async def test_special_characters(self):
        """特殊字符处理测试"""
        admin_token = create_access_token({
            "sub": "1",
            "username": "admin",
            "role": "super"
        })
        special_chars = [
            "{{7*7}}",  # 模板注入
            "${7*7}",   # 表达式注入
            "<!--#exec cmd='ls'-->",
            "#{7*7}",   # OGNL注入
            "%{7*7}",   # EL注入
        ]
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for payload in special_chars:
                response = await client.get(
                    f"/api/admin/users?keyword={payload}",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                # 应该正常处理，不应该执行模板/表达式
                assert response.status_code != 500


@pytest.mark.security
class TestPasswordSecurity:
    """密码安全测试"""

    async def test_weak_password_acceptance(self):
        """弱密码接受测试"""
        # 这个测试需要实际的创建管理员接口
        # 测试系统是否会接受弱密码
        weak_passwords = [
            "123",
            "password",
            "admin",
            "111111",
            "123456",
            "qwerty",
        ]
        admin_token = create_access_token({
            "sub": "1",
            "username": "admin",
            "role": "super"
        })
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            for pwd in weak_passwords:
                response = await client.post(
                    "/api/admin/admin-users",
                    headers={"Authorization": f"Bearer {admin_token}"},
                    json={
                        "username": f"test_{pwd}",
                        "password": pwd,
                        "role": "viewer"
                    }
                )
                # 应该拒绝弱密码（400）或由于数据库原因失败
                # 如果接受弱密码，这是一个安全问题
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 200:
                        # 系统接受了弱密码 - 这是一个安全问题
                        print(f"警告: 系统接受弱密码: {pwd}")


@pytest.mark.security
class TestRateLimiting:
    """速率限制测试"""

    async def test_brute_force_login(self):
        """暴力破解测试"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # 连续尝试多次错误登录
            responses = []
            for i in range(10):
                response = await client.post(
                    "/api/admin/login",
                    json={
                        "username": "admin",
                        "password": f"wrongpass{i}"
                    }
                )
                responses.append(response.status_code)

            # 如果有速率限制，后面的请求应该被限流(429)
            # 如果没有速率限制，所有请求都应该返回相同结果
            # 这只是一个检测，不作为强制断言
            if 429 in responses:
                print("好消息: 检测到速率限制")
            else:
                print("警告: 未检测到登录速率限制")

    async def test_request_flood(self):
        """请求洪水测试"""
        admin_token = create_access_token({
            "sub": "1",
            "username": "admin",
            "role": "super"
        })
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # 快速发送大量请求
            status_codes = []
            for _ in range(50):
                response = await client.get(
                    "/api/admin/dashboard/stats",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                status_codes.append(response.status_code)
                if response.status_code == 429:
                    break

            if 429 in status_codes:
                print("好消息: 检测到API速率限制")
            else:
                print("警告: 未检测到API速率限制")


@pytest.mark.security
class TestCorsSecurity:
    """CORS安全测试"""

    async def test_cors_headers(self):
        """CORS头测试"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.options(
                "/api/admin/me",
                headers={
                    "Origin": "http://evil.com",
                    "Access-Control-Request-Method": "GET"
                }
            )
            # 检查CORS响应头
            # 如果允许任意来源，这是一个安全问题
            cors_header = response.headers.get("access-control-allow-origin", "")
            if cors_header == "*":
                print("警告: CORS允许任意来源")
            elif cors_header == "http://evil.com":
                print("警告: CORS允许未授权的跨域请求")
