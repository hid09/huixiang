// 用户管理相关类型定义
import type { PaginatedResponse } from './common';

// 用户列表项
export interface UserListItem {
  id: string;  // UUID
  username: string;
  name?: string;  // 用户昵称
  created_at: string;
  records_count: number;
  diaries_count: number;
  last_active?: string;
}

// 用户详情
export interface UserDetail {
  id: string;
  username: string;
  name?: string;
  created_at: string;
  records_count: number;
  diaries_count: number;
  total_voice_count?: number;
  continuous_days?: number;
  last_active?: string;
  days_active: number;
}

// 录音记录
export interface RecordItem {
  id: string;  // UUID
  content: string;
  created_at: string;
  emotion_type: 'positive' | 'neutral' | 'negative' | 'mixed';
  asr_emotion?: string;
  mood_tag: string;
  input_type: string;
}

// 日记记录
export interface DiaryItem {
  id: string;  // UUID
  diary_date: string;
  emotion_type: string;
  mood_tag: string;
  keywords: string[] | string;
  what_happened: string[] | string;
  thoughts: string[] | string;
  small_discovery: string;
  records_count: number;
}

// 日记详情（含关联记录）
export interface DiaryDetail extends DiaryItem {
  user: {
    id: string;  // UUID
    username: string;
  };
  records: RecordItem[];
}

// 重新导出分页响应
export type { PaginatedResponse };

// 用户列表查询参数
export interface UserListParams {
  page?: number;
  page_size?: number;
  keyword?: string;
  start_date?: string;
  end_date?: string;
}
