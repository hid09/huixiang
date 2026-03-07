"""
用户服务单元测试
测试目标：验证用户注册、登录、认证流程
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.user_service import create_user_with_password, get_user_by_username
from app.core.auth import hash_password, verify_password


class TestPasswordHash:
    """密码哈希测试类"""

    def test_password_hash(self):
        """测试密码哈希生成"""
        password = "test123456"
        hashed = hash_password(password)
        
        assert hashed != password, "哈希后密码应与原密码不同"
        assert hashed.startswith("$2b$"), "bcrypt哈希应以$2b$开头"
        assert len(hashed) == 60, "bcrypt哈希长度应为60"

    def test_password_verify_correct(self):
        """测试正确密码验证"""
        password = "test123456"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) == True, "正确密码应验证通过"

    def test_password_verify_wrong(self):
        """测试错误密码验证"""
        password = "test123456"
        wrong_password = "wrong123456"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) == False, "错误密码应验证失败"

    def test_password_verify_empty(self):
        """测试空密码验证"""
        password = "test123456"
        hashed = hash_password(password)
        
        assert verify_password("", hashed) == False, "空密码应验证失败"


class TestUserService:
    """用户服务测试类"""

    def test_create_user_with_password(self, mock_db):
        """测试创建带密码用户"""
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        
        user = create_user_with_password(mock_db, "testuser", "password123", "测试用户")
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert user.username == "testuser"
        assert user.name == "测试用户"

    def test_get_user_by_username_not_found(self):
        """测试查找不存在的用户（使用 MagicMock）"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = get_user_by_username(mock_db, "nonexistent")
        assert result is None, "不存在的用户应返回None"

    def test_get_user_by_username_found(self):
        """测试查找存在的用户（使用 MagicMock）"""
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user

        result = get_user_by_username(mock_db, "testuser")
        assert result == mock_user, "应返回正确的用户"
