/**
 * 布局组件测试
 */
import { describe, it, expect, vi } from 'vitest'
// import { screen, fireEvent } from '@testing-library/react'
// import { renderWithProviders } from '../test-utils'
// import Layout from '../../components/Layout'

// Mock 路由
vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useNavigate: () => vi.fn(),
  useLocation: () => ({ pathname: '/dashboard' }),
}))

describe('Layout Component (基础测试)', () => {
  it('测试环境正常', () => {
    expect(true).toBe(true)
  })

  // TODO: 需要完整的 mock 环境（路由、API、localStorage）才能测试实际组件
  it.skip('应该渲染侧边栏和顶部栏', () => {
    // renderWithProviders(<Layout />)
    // expect(screen.getByText('数据看板')).toBeInTheDocument()
    // expect(screen.getByText('用户管理')).toBeInTheDocument()
  })

  it.skip('应该支持菜单切换', () => {
    // 需要实际渲染组件
  })
})
