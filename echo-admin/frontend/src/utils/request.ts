// HTTP 请求封装
import axios, { type AxiosError, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios';
import { message } from 'antd';

// API 基础 URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// 请求响应接口（导出给其他模块使用）
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 创建 axios 实例
const instance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('admin_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  (response: AxiosResponse) => {
    const { code, message: msg, data } = response.data;

    // code 200 表示成功
    if (code === 200) {
      return data;
    }

    // 其他 code 视为错误
    message.error(msg || '请求失败');
    return Promise.reject(new Error(msg || '请求失败'));
  },
  (error: AxiosError<ApiResponse>) => {
    const { response } = error;

    if (response) {
      const { status, data } = response;

      switch (status) {
        case 401:
          // 未授权，清除 token 并跳转登录
          message.error('登录已过期，请重新登录');
          localStorage.removeItem('admin_token');
          localStorage.removeItem('admin_user');
          window.location.href = '/login';
          break;
        case 403:
          message.error(data?.message || '没有权限访问');
          break;
        case 404:
          message.error(data?.message || '请求的资源不存在');
          break;
        case 500:
          message.error(data?.message || '服务器错误');
          break;
        default:
          message.error(data?.message || '请求失败');
      }
    } else if (error.code === 'ECONNABORTED') {
      message.error('请求超时，请检查网络连接');
    } else {
      message.error('网络错误，请检查网络连接');
    }

    return Promise.reject(error);
  }
);

// 类型安全的请求方法
const request = {
  get: <T>(url: string, config?: any): Promise<T> => instance.get(url, config),
  post: <T>(url: string, data?: any, config?: any): Promise<T> => instance.post(url, data, config),
  put: <T>(url: string, data?: any, config?: any): Promise<T> => instance.put(url, data, config),
  delete: <T>(url: string, config?: any): Promise<T> => instance.delete(url, config),
};

export default request;
