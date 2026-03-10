// 主布局组件 - 完全按原型设计
import React from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Modal } from 'antd';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import { clearAuth } from '@/utils/auth';
import styles from './Layout.module.less';

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [modal, contextHolder] = Modal.useModal();

  // 退出登录处理
  const handleLogout = () => {
    modal.confirm({
      title: '退出登录',
      content: '确定要退出登录吗？',
      okText: '确定',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        // 清除认证信息
        clearAuth();
        // 跳转到登录页
        navigate('/login');
      },
    });
  };

  // 获取页面标题
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/dashboard' || path === '/') return '数据看板';
    if (path.startsWith('/users')) return path.includes('/users/') ? '用户详情' : '用户管理';
    if (path.startsWith('/diaries')) return '日记详情';
    if (path === '/settings') return '系统设置';
    return '回响后台';
  };

  const title = getPageTitle();
  const showRefresh = location.pathname === '/dashboard';
  const showBackButton = location.pathname.startsWith('/users/') && location.pathname !== '/users';
  const handleBack = () => navigate('/users');

  return (
    <div className={styles.layout}>
      {/* 侧边栏 */}
      <Sidebar collapsed={false} />

      {/* 主内容区 */}
      <div className={styles.mainContent}>
        {/* 顶部栏 - 完全按原型 */}
        <Topbar
          title={title}
          onLogout={handleLogout}
          showRefresh={showRefresh}
          onRefresh={() => window.location.reload()}
          showBackButton={showBackButton}
          onBack={handleBack}
        />

        {/* 内容区 */}
        <div className={styles.content}>
          <Outlet />
        </div>
      </div>

      {/* Modal 容器 */}
      {contextHolder}
    </div>
  );
};

export { MainLayout };
export default MainLayout;
