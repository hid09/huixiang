/**
 * 登录页面 - 极简文学风格
 */
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useUserStore } from '@/stores/userStore'
import './Login.css'

export default function Login() {
  const navigate = useNavigate()
  const { login, isLoading } = useUserStore()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!username.trim() || !password.trim()) {
      setError('请填写完整信息')
      return
    }

    const result = await login(username.trim(), password.trim())
    if (result.success) {
      navigate('/')
    } else {
      setError(result.message || '登录失败')
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        {/* 标题区 */}
        <div className="login-header">
          <h1 className="login-title">回响</h1>
          <p className="login-subtitle">陪你听见自己</p>
        </div>

        {/* 引语 */}
        <div className="login-quote">
          每一次记录，都是与自己对话的开始
        </div>

        {/* 表单 */}
        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              className="form-input"
              placeholder="用户名"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <input
              type="password"
              className="form-input"
              placeholder="密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          {error && <div className="form-error">{error}</div>}

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? '登录中...' : '登录'}
          </button>
        </form>

        {/* 底部链接 */}
        <div className="login-footer">
          <span className="login-footer-text">还没有账号？</span>
          <Link to="/register" className="login-link">立即注册</Link>
        </div>
      </div>
    </div>
  )
}
