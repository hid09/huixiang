// 顶部栏组件 - 完全按原型设计
import React from 'react';
import { getUser } from '@/utils/auth';
import styles from './Topbar.module.less';

interface TopbarProps {
  title: string;
  onLogout: () => void;
  showRefresh?: boolean;
  onRefresh?: () => void;
  showBackButton?: boolean;
  onBack?: () => void;
}

const Topbar: React.FC<TopbarProps> = ({
  title,
  onLogout,
  showRefresh = false,
  onRefresh,
  showBackButton = false,
  onBack
}) => {
  const user = getUser();

  return (
    <header className={styles.topbar}>
      <div className={styles.topbarLeft}>
        {showBackButton && onBack && (
          <button className={styles.backBtn} onClick={onBack}>
            <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>
          </button>
        )}
        <h1 className={styles.topbarTitle}>{title}</h1>
      </div>
      <div className={styles.topbarRight}>
        {showRefresh && (
          <button className={styles.refreshBtn} onClick={onRefresh}>
            <svg className={styles.refreshIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            刷新
          </button>
        )}
        <button className={styles.logoutBtn} onClick={onLogout}>
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
          退出
        </button>
        <div className={styles.userInfo}>
          <div className={styles.userAvatar}>{user?.username?.charAt(0).toUpperCase() || '管'}</div>
          <div>
            <div className={styles.userName}>{user?.username || '管理员'}</div>
            <div className={styles.userRole}>{user?.role === 'super' ? '超级管理员' : '普通管理员'}</div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Topbar;
