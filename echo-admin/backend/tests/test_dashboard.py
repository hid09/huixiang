"""
数据看板模块测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.dashboard
class TestDashboardStats:
    """数据看板统计测试"""

    async def test_get_stats_success(self, client: AsyncClient, super_auth_headers: dict):
        """测试正常获取统计数据"""
        response = await client.get(
            "/api/admin/dashboard/stats",
            headers=super_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

        # 验证数据结构
        stats = data["data"]
        assert "overview" in stats
        assert "ai_health" in stats
        assert "trend_7d" in stats

        # 验证overview结构
        overview = stats["overview"]
        assert "total_users" in overview
        assert "dau_today" in overview
        assert "records_today" in overview
        assert "diaries_today" in overview
        assert all(isinstance(v, int) for v in overview.values())

        # 验证ai_health结构
        ai_health = stats["ai_health"]
        assert "success_count" in ai_health
        assert "fail_count" in ai_health
        assert "fail_rate" in ai_health

        # 验证trend_7d结构
        trend = stats["trend_7d"]
        assert "dates" in trend
        assert "new_users" in trend
        assert "active_users" in trend
        assert "records" in trend
        assert "diaries" in trend
        assert len(trend["dates"]) == 7

    async def test_get_stats_without_auth(self, client: AsyncClient):
        """测试无认证获取统计"""
        response = await client.get("/api/admin/dashboard/stats")

        assert response.status_code in [401, 403]

    @pytest.mark.security
    async def test_viewer_can_access(self, client: AsyncClient, viewer_auth_headers: dict):
        """测试普通管理员可以访问看板"""
        response = await client.get(
            "/api/admin/dashboard/stats",
            headers=viewer_auth_headers
        )

        assert response.status_code == 200
