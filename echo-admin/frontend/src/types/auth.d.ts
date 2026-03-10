// 认证相关类型定义
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: AdminUser;
}

export interface AdminUser {
  id: number;
  username: string;
  role: 'super' | 'viewer';
}
