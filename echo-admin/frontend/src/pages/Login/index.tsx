// 登录页面 - 完全按原型设计重写
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '@/services/auth';
import { setToken, setUser } from '@/utils/auth';
import { message } from 'antd';
import styles from './Login.module.less';

const Login: React.FC = () => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ username?: string; password?: string }>({});
  const navigate = useNavigate();

  const validateForm = (): boolean => {
    const newErrors: { username?: string; password?: string } = {};

    if (!username.trim()) {
      newErrors.username = '请输入用户名';
    }
    if (!password.trim()) {
      newErrors.password = '请输入密码';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      // 调用登录 API
      const data = await login({
        username: username.trim(),
        password: password,
      });

      // 保存 token 和用户信息
      setToken(data.token);
      setUser(data.user);

      // 处理记住我
      if (remember) {
        localStorage.setItem('admin_remember', 'true');
        localStorage.setItem('admin_username', username);
      } else {
        localStorage.removeItem('admin_remember');
        localStorage.removeItem('admin_username');
      }

      message.success('登录成功');

      // 跳转到首页
      navigate('/dashboard');
    } catch (error) {
      // 错误已在 request.ts 中处理
      console.error('登录失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.loginPage}>
      <div className={styles.loginContainer}>
        {/* Logo - 100%按原型 */}
        <div className={styles.loginLogo}>
          <div className={styles.logoIcon}>
            <svg viewBox="0 0 72 72">
              {/* 声波 Logo - 完全按原型 */}
              <rect className={styles.logoWave1} x="8" y="28" width="4" height="16" rx="2"/>
              <rect className={styles.logoWave2} x="18" y="22" width="4" height="28" rx="2"/>
              <rect className={styles.logoWave3} x="28" y="26" width="4" height="20" rx="2"/>
              <rect className={styles.logoWave2} x="38" y="20" width="4" height="32" rx="2"/>
              <rect className={styles.logoWave1} x="48" y="24" width="4" height="24" rx="2"/>
              <rect className={styles.logoWave3} x="58" y="30" width="4" height="12" rx="2"/>
            </svg>
          </div>
          <h1 className={styles.loginTitle}>回响后台</h1>
          <p className={styles.loginSubtitle}>ECHO ADMIN</p>
        </div>

        {/* 登录表单 - 原生HTML完全按原型 */}
        <form className={styles.loginForm} onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label className={styles.formLabel}>用户名</label>
            <input
              type="text"
              className={styles.formInput}
              placeholder="请输入用户名"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                setErrors({ ...errors, username: undefined });
              }}
              disabled={loading}
            />
            {errors.username && <span className={styles.errorText}>{errors.username}</span>}
          </div>

          <div className={styles.formGroup}>
            <label className={styles.formLabel}>密码</label>
            <input
              type="password"
              className={styles.formInput}
              placeholder="请输入密码"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setErrors({ ...errors, password: undefined });
              }}
              disabled={loading}
            />
            {errors.password && <span className={styles.errorText}>{errors.password}</span>}
          </div>

          <div className={styles.formRow}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                disabled={loading}
              />
              记住我
            </label>
          </div>

          <button
            type="submit"
            className={`${styles.btn} ${styles.btnPrimary}`}
            disabled={loading}
          >
            {loading ? '登录中...' : '登录系统'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
