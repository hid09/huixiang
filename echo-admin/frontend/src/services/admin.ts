// 管理员相关 API
import request from '@/utils/request';
import type { ApiResponse } from '@/types/common';

// 管理员用户类型
export interface AdminUser {
  id: number;
  username: string;
  role: 'super' | 'viewer';
  created_at: string;
  last_login?: string;
}

// 创建管理员请求
export interface CreateAdminRequest {
  username: string;
  password: string;
  role: 'super' | 'viewer';
}

// 重置密码请求
export interface ResetPasswordRequest {
  new_password: string;
}

/**
 * 获取管理员列表
 */
export const getAdminList = (): Promise<AdminUser[]> => {
  return request.get<AdminUser[]>('/admin/admin-users');
};

/**
 * 添加管理员
 */
export const createAdmin = (data: CreateAdminRequest): Promise<AdminUser> => {
  return request.post<AdminUser>('/admin/admin-users', data);
};

/**
 * 重置管理员密码
 */
export const resetAdminPassword = (
  id: number,
  data: ResetPasswordRequest
): Promise<void> => {
  return request.post<void>(`/admin/admin-users/${id}/reset-password`, data);
};
