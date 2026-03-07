"""
跨天逻辑单元测试
测试目标：验证 6:00-6:00 跨天规则
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.services.record_service import get_diary_date


class TestDiaryDate:
    """跨天逻辑测试类"""

    # ==================== 6:00-6:00 跨天规则 ====================
    def test_morning_after_6am(self):
        """测试早上6点后归属当天"""
        # 模拟早上8点
        mock_now = datetime(2026, 3, 6, 8, 0, 0)
        with patch('app.services.record_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            result = get_diary_date()
            assert result == "2026-03-06", f"8点应归属当天，实际: {result}"

    def test_noon_time(self):
        """测试中午12点归属当天"""
        mock_now = datetime(2026, 3, 6, 12, 0, 0)
        with patch('app.services.record_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            result = get_diary_date()
            assert result == "2026-03-06", f"12点应归属当天，实际: {result}"

    def test_evening_time(self):
        """测试晚上8点归属当天"""
        mock_now = datetime(2026, 3, 6, 20, 0, 0)
        with patch('app.services.record_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            result = get_diary_date()
            assert result == "2026-03-06", f"20点应归属当天，实际: {result}"

    def test_midnight(self):
        """测试凌晨0点归属前一天"""
        mock_now = datetime(2026, 3, 6, 0, 0, 0)
        with patch('app.services.record_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            result = get_diary_date()
            assert result == "2026-03-05", f"0点应归属前一天，实际: {result}"

    def test_early_morning_1am(self):
        """测试凌晨1点归属前一天"""
        mock_now = datetime(2026, 3, 6, 1, 0, 0)
        with patch('app.services.record_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            result = get_diary_date()
            assert result == "2026-03-05", f"1点应归属前一天，实际: {result}"

    def test_early_morning_559(self):
        """测试5:59归属前一天"""
        mock_now = datetime(2026, 3, 6, 5, 59, 59)
        with patch('app.services.record_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            result = get_diary_date()
            assert result == "2026-03-05", f"5:59应归属前一天，实际: {result}"

    # ==================== 边界时间测试 ====================
    def test_boundary_6am(self):
        """测试6点整归属当天"""
        mock_now = datetime(2026, 3, 6, 6, 0, 0)
        with patch('app.services.record_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            result = get_diary_date()
            assert result == "2026-03-06", f"6点整应归属当天，实际: {result}"

    def test_boundary_559(self):
        """测试5:59归属前一天"""
        mock_now = datetime(2026, 3, 6, 5, 59, 0)
        with patch('app.services.record_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            result = get_diary_date()
            assert result == "2026-03-05", f"5:59应归属前一天，实际: {result}"

    # ==================== 跨月跨年 ====================
    def test_cross_month(self):
        """测试跨月情况"""
        # 4月1日凌晨2点，应归属3月31日
        mock_now = datetime(2026, 4, 1, 2, 0, 0)
        with patch('app.services.record_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            result = get_diary_date()
            assert result == "2026-03-31", f"跨月应正确，实际: {result}"

    def test_cross_year(self):
        """测试跨年情况"""
        # 1月1日凌晨3点，应归属12月31日
        mock_now = datetime(2026, 1, 1, 3, 0, 0)
        with patch('app.services.record_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            result = get_diary_date()
            assert result == "2025-12-31", f"跨年应正确，实际: {result}"
