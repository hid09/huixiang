// 应用入口组件
import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Spin } from 'antd';
import Login from './pages/Login';
import MainLayout from './components/Layout';
import Dashboard from './pages/Dashboard';
import UserList from './pages/Users/UserList';
import UserList_UserDetail from './pages/Users/UserDetail';
import DiaryList_DiaryDetail from './pages/Diaries/DiaryDetail';
import Settings from './pages/Settings';
import './styles/global.less';

// 加载中组件
const PageLoading: React.FC = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
    <Spin size="large" />
  </div>
);

// 路由守卫组件
const ProtectedRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const token = localStorage.getItem('admin_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const App: React.FC = () => {
  return (
    <Suspense fallback={<PageLoading />}>
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={<Login />} />

        {/* 受保护路由 */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="users" element={<UserList />} />
          <Route path="users/:id" element={<UserList_UserDetail />} />
          <Route path="diaries/:id" element={<DiaryList_DiaryDetail />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* 404 重定向 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  );
};

export default App;
