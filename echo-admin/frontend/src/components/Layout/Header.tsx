// 顶部栏组件
import React from 'react';
import { Layout, Dropdown, Avatar, Space } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { getUser } from '@/utils/auth';
import styles from './Header.module.less';

const { Header: AntHeader } = Layout;

interface HeaderProps {
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLogout }) => {
  const user = getUser();

  // 下拉菜单
  const menuItems: MenuProps['items'] = [
    {
      key: 'profile',
      label: (
        <div className={styles.profileInfo}>
          <div className={styles.username}>{user?.username}</div>
          <div className={styles.role}>
            {user?.role === 'super' ? '超级管理员' : '普通管理员'}
          </div>
        </div>
      ),
      disabled: true,
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      label: '退出登录',
      onClick: onLogout,
      danger: true,
    },
  ];

  return (
    <AntHeader className={styles.header}>
      {/* 左侧：页面标题 */}
      <div className={styles.title}>回响后台管理系统</div>

      {/* 右侧：用户信息 */}
      <Dropdown menu={{ items: menuItems }} placement="bottomRight" trigger={['click']}>
        <Space className={styles.userTrigger} >
          <Avatar
            size="small"
            icon={<UserOutlined />}
            style={{ backgroundColor: '#4ecdc4' }}
          />
          <span className={styles.username}>{user?.username}</span>
        </Space>
      </Dropdown>
    </AntHeader>
  );
};

export default Header;
