/**
 * 我的页面 - 基于原型设计
 */
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUserStore } from '@/stores/userStore'
import './Profile.css'

// 用户图标
const UserIcon = () => (
  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" strokeWidth="2">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
)

export default function Profile() {
  const navigate = useNavigate()
  const { user, stats, refreshUser, refreshStats, logout } = useUserStore()

  useEffect(() => {
    refreshUser()
    refreshStats()
  }, [refreshUser, refreshStats])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="profile-page">
      {/* 头部区域 */}
      <div className="profile-header">
        <div className="profile-avatar">
          <UserIcon />
        </div>
        <div className="profile-name">你好，{user?.username || user?.name || '用户'}</div>
        <div className="profile-desc">已记录 {stats?.total_record_days || 0} 天</div>
      </div>

      {/* 统计卡片 */}
      <div className="stats-card">
        {/* 主数字 - 累计天数 */}
        <div className="stats-main">
          <div className="stats-label">累计记录</div>
          <div className="stats-number">
            {stats?.total_record_days || 0}<span>天</span>
          </div>
        </div>

        {/* 单行三列 */}
        <div className="stats-row">
          <div className="stats-item">
            <span className="stats-item-value">{stats?.continuous_days || 0}天 🔥</span>
            <span className="stats-item-label">连续记录</span>
          </div>
          <div className="stats-item">
            <span className="stats-item-value">{stats?.total_voice_count || 0}</span>
            <span className="stats-item-label">语音条数</span>
          </div>
          <div className="stats-item">
            <span className="stats-item-value">{stats?.this_month_percentage || 0}%</span>
            <span className="stats-item-label">本月完成率</span>
          </div>
        </div>
      </div>

      {/* 功能入口 */}
      <div className="settings-section">
        <div className="settings-item" onClick={() => navigate('/growth')}>
          <div className="settings-item-left">
            <div className="settings-item-icon">📊</div>
            <span className="settings-item-text">成长记录</span>
          </div>
          <span className="settings-item-arrow">→</span>
        </div>
        <div className="settings-item">
          <div className="settings-item-left">
            <div className="settings-item-icon">💡</div>
            <span className="settings-item-text">过去的我说</span>
          </div>
          <span className="settings-item-arrow">→</span>
        </div>
      </div>

      {/* 设置入口 */}
      <div className="settings-section">
        <div className="settings-item">
          <div className="settings-item-left">
            <div className="settings-item-icon">⚙️</div>
            <span className="settings-item-text">设置</span>
          </div>
          <span className="settings-item-arrow">→</span>
        </div>
        <div className="settings-item logout" onClick={handleLogout}>
          <div className="settings-item-left">
            <div className="settings-item-icon">🚪</div>
            <span className="settings-item-text">退出登录</span>
          </div>
        </div>
      </div>

      {/* 版本信息 */}
      <div className="version-info">
        回响 v1.0.0<br/>
        回响，陪你听见自己
      </div>
    </div>
  )
}
