/**
 * 注册页面 - 极简文学风格
 */
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useUserStore } from '@/stores/userStore'
import './Register.css'

export default function Register() {
  const navigate = useNavigate()
  const { register, isLoading } = useUserStore()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!username.trim() || !password.trim()) {
      setError('请填写用户名和密码')
      return
    }

    if (username.length < 2 || username.length > 20) {
      setError('用户名需要2-20个字符')
      return
    }

    if (password.length < 6) {
      setError('密码至少6位')
      return
    }

    if (password !== confirmPassword) {
      setError('两次密码不一致')
      return
    }

    const result = await register(username.trim(), password.trim(), name.trim() || '回响用户')
    if (result.success) {
      navigate('/')
    } else {
      setError(result.message || '注册失败')
    }
  }

  return (
    <div className="register-page">
      <div className="register-card">
        {/* 标题区 */}
        <div className="register-header">
          <h1 className="register-title">回响</h1>
          <p className="register-subtitle">开始你的记录之旅</p>
        </div>

        {/* 表单 */}
        <form className="register-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">用户名</label>
            <input
              type="text"
              className="form-input"
              placeholder="2-20个字符"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label className="form-label">密码</label>
            <input
              type="password"
              className="form-input"
              placeholder="至少6位"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label className="form-label">确认密码</label>
            <input
              type="password"
              className="form-input"
              placeholder="再次输入密码"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label className="form-label">昵称（可选）</label>
            <input
              type="text"
              className="form-input"
              placeholder="想怎么称呼你？"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          {error && <div className="form-error">{error}</div>}

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? '注册中...' : '注册'}
          </button>
        </form>

        {/* 底部链接 */}
        <div className="register-footer">
          <span className="register-footer-text">已有账号？</span>
          <Link to="/login" className="register-link">立即登录</Link>
        </div>
      </div>
    </div>
  )
}
