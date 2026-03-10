// 数据看板相关类型定义

// 概览数据
export interface OverviewStats {
  total_users: number;
  dau_today: number;
  records_today: number;
  diaries_today: number;
}

// AI 健康度
export interface AIHealth {
  success_count: number;
  fail_count: number;
  fail_rate: number;
}

// 7天趋势数据
export interface Trend7D {
  dates: string[];
  new_users: number[];
  active_users: number[];
  records: number[];
  diaries: number[];
}

// 看板完整数据
export interface DashboardData {
  overview: OverviewStats;
  ai_health: AIHealth;
  trend_7d: Trend7D;
}
