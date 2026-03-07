/**
 * 回响 - API服务封装
 */
import axios, { type AxiosInstance, type AxiosError } from 'axios'

// API响应类型
export interface ApiResponse<T> {
  success: boolean
  data: T
  message: string
}

// 错误响应类型
export interface ApiError {
  code: number
  message: string
}

// Token响应类型
export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器 - 自动添加Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('echo_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理401
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error: AxiosError<ApiResponse<unknown>>) => {
    if (error.response?.status === 401) {
      // Token过期，清除本地存储并跳转登录
      localStorage.removeItem('echo_token')
      window.location.href = '/login'
    }
    const message = error.response?.data?.message || error.message || '网络错误'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

// ==================== 用户相关API ====================

export interface User {
  id: string
  username: string | null
  name: string
  avatar: string | null
  timezone: string
  diary_time: string
  total_record_days: number
  total_voice_count: number
  continuous_days: number
  longest_continuous_days: number
  last_record_date: string | null
  created_at: string
}

export interface UserStats {
  total_record_days: number
  total_voice_count: number
  continuous_days: number
  longest_continuous_days: number
  this_month_days: number
  this_month_percentage: number
}

export const userApi = {
  // 登录
  login: (username: string, password: string) =>
    api.post<unknown, ApiResponse<TokenResponse>>('/user/login', { username, password }),

  // 注册
  register: (username: string, password: string, name?: string) =>
    api.post<unknown, ApiResponse<TokenResponse>>('/user/register', { username, password, name }),

  // 退出
  logout: () =>
    api.post<unknown, ApiResponse<null>>('/user/logout'),

  // 获取当前用户信息（需要认证）
  getMe: () =>
    api.get<unknown, ApiResponse<User>>('/user/me'),

  // 获取当前用户统计（需要认证）
  getStatsMe: () =>
    api.get<unknown, ApiResponse<UserStats>>('/user/stats/me'),

  // 更新当前用户信息（需要认证）
  updateProfileMe: (data: Partial<User>) =>
    api.put<unknown, ApiResponse<User>>('/user/profile/me', data),
}

// ==================== 记录相关API ====================

export interface Record {
  id: string
  user_id: string
  transcribed_text: string | null
  primary_emotion: string | null
  emotion_intensity: number
  topic_tags: string | null
  audio_duration: number
  recorded_at: string
  created_at: string
}

export interface RecordListResponse {
  items: Record[]
  total: number
  page: number
  page_size: number
}

export const recordApi = {
  // 创建文字记录（需要认证）
  createTextByToken: (text: string, localTimestamp?: string, localDate?: string) =>
    api.post<unknown, ApiResponse<Record>>('/records/text', {
      text,
      local_timestamp: localTimestamp,
      local_date: localDate
    }),

  // 获取记录列表（需要认证）
  getListByToken: (date?: string, page: number = 1, pageSize: number = 20) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
    if (date) params.append('date', date)
    return api.get<unknown, ApiResponse<RecordListResponse>>(`/records?${params}`)
  },

  // 获取今日记录（需要认证）
  getTodayByToken: () =>
    api.get<unknown, ApiResponse<Record[]>>('/records/today'),

  // 获取单条记录（需要认证）
  getByIdWithToken: (recordId: string) =>
    api.get<unknown, ApiResponse<Record>>(`/records/${recordId}`),

  // 语音转写（返回转写结果和分析）
  transcribeVoice: async (audioBlob: Blob) => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')
    const response = await fetch('/api/records/voice/transcribe', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('echo_token')}`
      },
      body: formData
    })
    return response.json()
  },

  // 确认语音记录（转写后编辑版，会对编辑后的文本做情绪分析）
  confirmVoiceRecord: (text: string, localDate?: string) =>
    api.post<unknown, ApiResponse<Record>>('/records/voice/confirm', {
      text,
      local_date: localDate
    }),

  // 创建语音记录（完整流程：转写 + 分析 + 保存）
  createVoiceRecord: async (audioBlob: Blob, audioDuration: number, localDate?: string) => {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.webm')
    formData.append('audio_duration', String(audioDuration))
    if (localDate) {
      formData.append('local_date', localDate)
    }
    const response = await fetch('/api/records/voice', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('echo_token')}`
      },
      body: formData
    })
    return response.json()
  },
}

// ==================== 日记相关API ====================

export interface CognitiveChange {
  has_change: boolean
  changes: [{
    type: string
    topic: string
    before: string
    after: string
    evidence: string
  }]
  insight: string
}

export interface Diary {
  id: string
  user_id: string
  diary_date: string
  // v3.0 字段
  mood_tag: string
  emotion_type: string
  keywords: string[]
  what_happened: string[]
  thoughts: string[]
  small_discovery: string | null
  closing: string
  tomorrow_hint: string | null
  cognitive_change: CognitiveChange | null
  // 元数据
  record_day_count: number
  generated_at: string
}

export interface DiaryListResponse {
  items: Diary[]
  total: number
  page: number
  page_size: number
}

export const diaryApi = {
  // 生成日记
  generate: (date: string) =>
    api.post<unknown, ApiResponse<Diary>>('/diaries/generate', { date }),

  // 获取日记列表
  getList: (page: number = 1, pageSize: number = 20) =>
    api.get<unknown, ApiResponse<DiaryListResponse>>(`/diaries?page=${page}&page_size=${pageSize}`),

  // 获取指定日期的日记
  getByDate: (date: string) =>
    api.get<unknown, ApiResponse<Diary>>(`/diaries/${date}`),

  // 获取连续未记录天数（供首页渐进式关怀使用）
  getConsecutiveEmptyDays: () =>
    api.get<unknown, ApiResponse<{ consecutive_empty_days: number }>>('/diaries/stats/empty-days'),
}

// ==================== 周回顾相关API ====================

export interface WeeklyReview {
  week_start: string
  week_end: string
  record_days: number
  voice_count: number
  dominant_emotion: string
  dominant_emotion_name: string
  emotion_trend: Array<{
    day: string
    emoji: string
    emotion_type: string
  }>
  positive_ratio: number
  keywords: Array<{
    text: string
    large: boolean
  }>
  suggestions: string[]
}

export const reviewsApi = {
  // 获取本周周回顾
  getWeekly: () =>
    api.get<unknown, ApiResponse<WeeklyReview>>('/reviews/weekly'),
}

export default api
