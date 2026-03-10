// 侧边栏导航组件 - 完全按原型设计
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styles from './Sidebar.module.less';

interface SidebarProps {
  collapsed: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed }) => {
  const navigate = useNavigate();
  const location = useLocation();

  // 判断当前激活的菜单
  const isActive = (path: string) => {
    if (path === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  // 菜单配置
  const menuItems = [
    {
      key: 'dashboard',
      path: '/dashboard',
      label: '数据看板',
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
        </svg>
      ),
    },
    {
      key: 'users',
      path: '/users',
      label: '用户管理',
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
        </svg>
      ),
    },
    {
      key: 'settings',
      path: '/settings',
      label: '系统设置',
      icon: (
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
      ),
    },
  ];

  const handleMenuClick = (path: string) => {
    navigate(path);
  };

  return (
    <aside className={styles.sidebar}>
      {/* Logo 区域 */}
      <div className={styles.sidebarLogo}>
        <div className={styles.sidebarLogoText}>
          <svg className={styles.sidebarLogoIcon} viewBox="0 0 32 32">
            <rect fill="#4ecdc4" x="4" y="12" width="3" height="8" rx="1.5"/>
            <rect fill="#4ecdc4" x="9" y="8" width="3" height="16" rx="1.5"/>
            <rect fill="#4ecdc4" x="14" y="10" width="3" height="12" rx="1.5"/>
            <rect fill="#4ecdc4" x="19" y="6" width="3" height="20" rx="1.5"/>
            <rect fill="#4ecdc4" x="24" y="11" width="3" height="10" rx="1.5"/>
          </svg>
          回响后台
        </div>
      </div>

      {/* 导航菜单 */}
      <nav className={styles.sidebarNav}>
        {menuItems.map((item) => (
          <a
            key={item.key}
            className={`${styles.navItem} ${isActive(item.path) ? styles.navItemActive : ''}`}
            onClick={() => handleMenuClick(item.path)}
          >
            <span className={styles.navIcon}>{item.icon}</span>
            {item.label}
          </a>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
