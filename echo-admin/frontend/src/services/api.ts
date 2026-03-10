// API 基础配置
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// 通用分页参数
export interface PageParams {
  page?: number;
  page_size?: number;
}

// 通用分页响应
export interface PaginatedResponse<T> {
  total: number;
  items: T[];
}
