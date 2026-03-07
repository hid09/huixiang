/**
 * 路由守卫 - 保护需要认证的页面
 */
import { Navigate, useLocation } from 'react-router-dom'
import { useUserStore } from '@/stores/userStore'

interface PrivateRouteProps {
  children: React.ReactNode
}

export default function PrivateRoute({ children }: PrivateRouteProps) {
  const location = useLocation()
  const token = useUserStore((state) => state.token)

  // 无token直接跳转登录
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}
