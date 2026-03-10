// 数据看板相关 API
import request from '@/utils/request';
import type { DashboardData } from '@/types/dashboard';

/**
 * 获取看板统计数据
 */
export const getDashboardStats = (): Promise<DashboardData> => {
  return request.get<DashboardData>('/admin/dashboard/stats');
};
