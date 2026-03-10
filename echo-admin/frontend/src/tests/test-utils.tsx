/**
 * 测试工具函数
 */
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'

/**
 * 渲染带有基础 Provider 的组件
 */
export function renderWithProviders(ui: React.ReactElement) {
  return render(
    <BrowserRouter>
      <ConfigProvider locale={zhCN}>
        {ui}
      </ConfigProvider>
    </BrowserRouter>
  )
}

/**
 * 创建 Mock 函数类型
 */
export type MockFunction<T extends (...args: any[]) => any> = {
  (...args: Parameters<T>): ReturnType<T>
  mock: {
    calls: Parameters<T>[]
    results: ReturnType<T>[]
  }
}
