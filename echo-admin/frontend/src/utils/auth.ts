// Token 管理工具

const TOKEN_KEY = 'admin_token';
const USER_KEY = 'admin_user';

export interface AdminUser {
  id: number;
  username: string;
  role: 'super' | 'viewer';
}

/**
 * 获取 Token
 */
export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * 设置 Token
 */
export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

/**
 * 移除 Token
 */
export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

/**
 * 获取当前登录用户信息
 */
export const getUser = (): AdminUser | null => {
  const userStr = localStorage.getItem(USER_KEY);
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
  return null;
};

/**
 * 设置当前登录用户信息
 */
export const setUser = (user: AdminUser): void => {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

/**
 * 移除当前登录用户信息
 */
export const removeUser = (): void => {
  localStorage.removeItem(USER_KEY);
};

/**
 * 清除所有认证信息
 */
export const clearAuth = (): void => {
  removeToken();
  removeUser();
};

/**
 * 检查是否已登录
 */
export const isAuthenticated = (): boolean => {
  return !!getToken();
};

/**
 * 检查是否是超级管理员
 */
export const isSuperAdmin = (): boolean => {
  const user = getUser();
  return user?.role === 'super';
};
