// 认证相关 API
import request from '@/utils/request';
import type { LoginRequest, LoginResponse, AdminUser } from '@/types/auth';

/**
 * 管理员登录
 */
export const login = (data: LoginRequest): Promise<LoginResponse> => {
  return request.post<LoginResponse>('/admin/login', data);
};

/**
 * 管理员退出
 */
export const logout = (): Promise<void> => {
  return request.post('/admin/logout');
};

/**
 * 获取当前登录用户信息
 */
export const getCurrentUser = (): Promise<AdminUser> => {
  return request.get<AdminUser>('/admin/me');
};
