/**
 * 测试 Mock 数据
 */

// Mock 用户数据
export const mockUsers = [
  {
    id: 1,
    username: 'testuser001',
    phone: '13800138000',
    created_at: '2026-01-01T10:00:00',
    records_count: 150,
    diaries_count: 45,
    last_active: '2026-03-09T15:30:00'
  },
  {
    id: 2,
    username: 'testuser002',
    phone: '13800138001',
    created_at: '2026-01-02T10:00:00',
    records_count: 80,
    diaries_count: 20,
    last_active: '2026-03-08T12:00:00'
  }
]

// Mock 看板统计数据
export const mockDashboardStats = {
  overview: {
    total_users: 1234,
    dau_today: 56,
    records_today: 128,
    diaries_today: 45
  },
  ai_health: {
    success_count: 48,
    fail_count: 2,
    fail_rate: 4.0
  },
  trend_7d: {
    dates: ['03-03', '03-04', '03-05', '03-06', '03-07', '03-08', '03-09'],
    new_users: [12, 8, 15, 10, 6, 14, 9],
    active_users: [45, 52, 48, 60, 55, 58, 56],
    records: [89, 102, 95, 120, 108, 115, 128],
    diaries: [34, 40, 38, 45, 42, 44, 45]
  }
}

// Mock 录音记录
export const mockRecords = [
  {
    id: 1001,
    content: '今天天气真不错',
    created_at: '2026-03-09T15:30:00',
    emotion_type: 'positive',
    asr_emotion: 'happy',
    mood_tag: '开心',
    input_type: '情绪表达'
  }
]

// Mock 日记
export const mockDiaries = [
  {
    id: 201,
    diary_date: '2026-03-09',
    emotion_type: 'positive',
    mood_tag: '平静',
    keywords: ['天气', '散步', '咖啡'],
    what_happened: '今天天气不错，出去散步了',
    thoughts: '感觉心情放松了很多',
    small_discovery: '公园的樱花开了',
    records_count: 3
  }
]

// Mock 管理员
export const mockAdminUsers = [
  {
    id: 1,
    username: 'admin',
    role: 'super',
    created_at: '2026-01-01T10:00:00'
  },
  {
    id: 2,
    username: 'viewer',
    role: 'viewer',
    created_at: '2026-01-02T10:00:00'
  }
]
