/**
 * 回响 - 用户状态管理
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { type User, type UserStats, userApi } from '@/services/api'

interface UserState {
  // 状态
  token: string | null
  user: User | null
  stats: UserStats | null
  isLoading: boolean
  isInitialized: boolean

  // 操作
  login: (username: string, password: string) => Promise<{ success: boolean; message?: string }>
  register: (username: string, password: string, name?: string) => Promise<{ success: boolean; message?: string }>
  logout: () => void
  refreshUser: () => Promise<void>
  refreshStats: () => Promise<void>
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      stats: null,
      isLoading: false,
      isInitialized: false,

      login: async (username: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await userApi.login(username, password)
          if (response.success && response.data) {
            const { access_token, user } = response.data
            localStorage.setItem('echo_token', access_token)
            set({
              token: access_token,
              user: user,
              isInitialized: true
            })
            // 获取统计
            try {
              const statsResponse = await userApi.getStatsMe()
              if (statsResponse.success) {
                set({ stats: statsResponse.data })
              }
            } catch (e) {
              console.error('获取统计失败:', e)
            }
            return { success: true }
          }
          return { success: false, message: response.message || '登录失败' }
        } catch (error: unknown) {
          const err = error as { response?: { data?: { message?: string } } }
          return { success: false, message: err.response?.data?.message || '网络错误' }
        } finally {
          set({ isLoading: false })
        }
      },

      register: async (username: string, password: string, name?: string) => {
        set({ isLoading: true })
        try {
          const response = await userApi.register(username, password, name)
          if (response.success && response.data) {
            const { access_token, user } = response.data
            localStorage.setItem('echo_token', access_token)
            set({
              token: access_token,
              user: user,
              isInitialized: true
            })
            return { success: true }
          }
          return { success: false, message: response.message || '注册失败' }
        } catch (error: unknown) {
          const err = error as { response?: { data?: { message?: string } } }
          return { success: false, message: err.response?.data?.message || '网络错误' }
        } finally {
          set({ isLoading: false })
        }
      },

      logout: () => {
        localStorage.removeItem('echo_token')
        set({ token: null, user: null, stats: null, isInitialized: false })
      },

      refreshUser: async () => {
        const { token } = get()
        if (!token) return

        try {
          const response = await userApi.getMe()
          if (response.success) {
            set({ user: response.data })
          }
        } catch (error) {
          console.error('获取用户信息失败:', error)
        }
      },

      refreshStats: async () => {
        const { token } = get()
        if (!token) return

        try {
          const response = await userApi.getStatsMe()
          if (response.success) {
            set({ stats: response.data })
          }
        } catch (error) {
          console.error('获取统计失败:', error)
        }
      },
    }),
    {
      name: 'echo-user-store',
      partialize: (state) => ({ token: state.token }),
    }
  )
)
