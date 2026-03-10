// 路由配置
import { lazy } from 'react';

// 懒加载页面组件
const Login = lazy(() => import('@/pages/Login'));
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const UserList = lazy(() => import('@/pages/Users/UserList'));
const UserDetail = lazy(() => import('@/pages/Users/UserDetail'));
const DiaryDetail = lazy(() => import('@/pages/Diaries/DiaryDetail'));
const Settings = lazy(() => import('@/pages/Settings'));

// 主布局组件（非懒加载）
import { MainLayout } from '@/components/Layout';

export interface RouteConfig {
  path: string;
  component?: React.ComponentType;
  element?: React.ReactElement;
  children?: RouteConfig[];
  redirect?: string;
  isPublic?: boolean;
}

// 路由配置
const routes: RouteConfig[] = [
  {
    path: '/login',
    component: Login,
    isPublic: true,
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: 'dashboard',
        component: Dashboard,
      },
      {
        path: 'users',
        component: UserList,
      },
      {
        path: 'users/:id',
        component: UserDetail,
      },
      {
        path: 'diaries/:id',
        component: DiaryDetail,
      },
      {
        path: 'settings',
        component: Settings,
      },
    ],
  },
];

export default routes;
