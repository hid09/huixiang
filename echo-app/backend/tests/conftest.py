"""
测试配置文件
"""
import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def mock_db():
    """创建内存数据库会话"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    session.close()


@pytest.fixture
def mock_user_id():
    """模拟用户ID"""
    return "test-user-id-12345"


@pytest.fixture
def sample_records():
    """测试用记录样本"""
    return [
        {"text": "今天完成了一个重要功能开发", "emotion": "positive"},
        {"text": "产品开发还是要遵循定好的规则", "emotion": "neutral"},
        {"text": "终于把项目做完了，虽然累但挺有成就感", "emotion": "positive"},
    ]
