// 用户管理相关 API
import request from '@/utils/request';
import type { PaginatedResponse } from '@/types/common';
import type {
  UserListItem,
  UserDetail,
  RecordItem,
  DiaryItem,
  DiaryDetail,
  UserListParams,
} from '@/types/user';

/**
 * 获取用户列表
 */
export const getUserList = (params: UserListParams): Promise<PaginatedResponse<UserListItem>> => {
  return request.get<PaginatedResponse<UserListItem>>('/admin/users', { params });
};

/**
 * 获取用户详情
 */
export const getUserDetail = (id: string): Promise<UserDetail> => {
  return request.get<UserDetail>(`/admin/users/${id}`);
};

/**
 * 获取用户录音记录列表
 */
export const getUserRecords = (id: string, params: { page?: number; page_size?: number }): Promise<PaginatedResponse<RecordItem>> => {
  return request.get<PaginatedResponse<RecordItem>>(`/admin/users/${id}/records`, { params });
};

/**
 * 获取用户日记列表
 */
export const getUserDiaries = (id: string, params: { page?: number; page_size?: number }): Promise<PaginatedResponse<DiaryItem>> => {
  return request.get<PaginatedResponse<DiaryItem>>(`/admin/users/${id}/diaries`, { params });
};

/**
 * 获取日记详情
 */
export const getDiaryDetail = (id: string): Promise<DiaryDetail> => {
  return request.get<DiaryDetail>(`/admin/diaries/${id}`);
};

/**
 * 导出用户列表
 */
export const exportUsers = (): Promise<Blob> => {
  return request.get('/admin/users/export', {
    responseType: 'blob',
  });
};

/**
 * 重置用户密码
 */
export const resetUserPassword = (id: string): Promise<{ new_password: string }> => {
  return request.post<{ new_password: string }>(`/admin/users/${id}/reset-password`);
};
