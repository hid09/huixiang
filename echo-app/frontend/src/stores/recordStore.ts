/**
 * 回响 - 记录状态管理
 */
import { create } from 'zustand'
import { type Record as RecordType, recordApi } from '@/services/api'
import { useUserStore } from './userStore'

interface RecordState {
  // 状态
  todayRecords: RecordType[]
  records: RecordType[]
  isLoading: boolean
  isSubmitting: boolean

  // 操作
  fetchTodayRecords: () => Promise<void>
  fetchRecords: () => Promise<void>
  submitTextRecord: (text: string) => Promise<boolean>
  clearRecords: () => void
}

export const useRecordStore = create<RecordState>((set, get) => ({
  todayRecords: [],
  records: [],
  isLoading: false,
  isSubmitting: false,

  fetchRecords: async () => {
    const token = useUserStore.getState().token
    if (!token) return

    set({ isLoading: true })
    try {
      const response = await recordApi.getListByToken()
      if (response.success) {
        set({ records: response.data.items })
      }
    } catch (error) {
      console.error('获取记录列表失败:', error)
    } finally {
      set({ isLoading: false })
    }
  },

  fetchTodayRecords: async () => {
    const token = useUserStore.getState().token
    if (!token) return

    set({ isLoading: true })
    try {
      const response = await recordApi.getTodayByToken()
      if (response.success) {
        // 按时间倒序排列（最新的在前面）
        const sortedRecords = [...response.data].sort((a, b) =>
          new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime()
        )
        set({ todayRecords: sortedRecords })
      }
    } catch (error) {
      console.error('获取今日记录失败:', error)
    } finally {
      set({ isLoading: false })
    }
  },

  submitTextRecord: async (text: string) => {
    const token = useUserStore.getState().token
    if (!token || !text.trim()) return false

    set({ isSubmitting: true })
    try {
      // 获取本地日期 YYYY-MM-DD（用于日记分组，6:00-6:00 划分）
      // 凌晨 0:00-5:59 的记录归入前一天
      const now = new Date()
      let localDate: string
      if (now.getHours() < 6) {
        // 凌晨 0-6 点，归入前一天
        const yesterday = new Date(now)
        yesterday.setDate(yesterday.getDate() - 1)
        localDate = yesterday.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        }).replace(/\//g, '-')
      } else {
        // 6 点之后，归入当天
        localDate = now.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        }).replace(/\//g, '-')
      }

      const localTimestamp = new Date().toISOString()

      const response = await recordApi.createTextByToken(text.trim(), localTimestamp, localDate)
      if (response.success) {
        await get().fetchTodayRecords()
        await useUserStore.getState().refreshStats()
        return true
      }
      return false
    } catch (error) {
      console.error('提交记录失败:', error)
      return false
    } finally {
      set({ isSubmitting: false })
    }
  },

  clearRecords: () => {
    set({ todayRecords: [], records: [] })
  },
}))
