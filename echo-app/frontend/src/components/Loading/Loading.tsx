/**
 * 加载状态组件
 */
import { SpinLoading } from 'antd-mobile'
import './Loading.css'

interface LoadingProps {
  text?: string
  fullScreen?: boolean
}

export default function Loading({ text = '加载中...', fullScreen = false }: LoadingProps) {
  if (fullScreen) {
    return (
      <div className="loading-fullscreen">
        <SpinLoading color="primary" />
        <p className="loading-text">{text}</p>
      </div>
    )
  }

  return (
    <div className="loading-inline">
      <SpinLoading color="primary" />
      <span className="loading-text">{text}</span>
    </div>
  )
}
