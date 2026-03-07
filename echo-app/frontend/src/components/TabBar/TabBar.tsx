/**
 * 底部导航栏组件 - 基于原型设计
 */
import { NavLink } from 'react-router-dom'
import './TabBar.css'

// 首页图标
const HomeIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" strokeWidth="2">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
    <polyline points="9 22 9 12 15 12 15 22"></polyline>
  </svg>
)

// 日记图标
const DiaryIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" strokeWidth="2">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
  </svg>
)

// 成长图标
const GrowthIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" strokeWidth="2">
    <line x1="18" y1="20" x2="18" y2="10"></line>
    <line x1="12" y1="20" x2="12" y2="4"></line>
    <line x1="6" y1="20" x2="6" y2="14"></line>
  </svg>
)

// 我的图标
const ProfileIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" strokeWidth="2">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
)

const tabs = [
  { path: '/', icon: HomeIcon, label: '首页' },
  { path: '/diary', icon: DiaryIcon, label: '日记' },
  { path: '/growth', icon: GrowthIcon, label: '成长' },
  { path: '/profile', icon: ProfileIcon, label: '我的' },
]

export default function TabBar() {
  return (
    <nav className="tab-bar">
      {tabs.map(({ path, icon: Icon, label }) => (
        <NavLink
          key={path}
          to={path}
          className={({ isActive }) => `tab-bar-item ${isActive ? 'active' : ''}`}
        >
          <Icon />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  )
}
