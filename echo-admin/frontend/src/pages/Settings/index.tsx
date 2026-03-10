// 系统设置页 - 完全按原型设计（移除Ant Design）
import React, { useEffect, useState } from 'react';
import dayjs from 'dayjs';
import { getAdminList, createAdmin, resetAdminPassword, type AdminUser } from '@/services/admin';
import { getUser } from '@/utils/auth';
import styles from './Settings.module.less';

const Settings: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [admins, setAdmins] = useState<AdminUser[]>([]);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [resetModalVisible, setResetModalVisible] = useState(false);
  const [selectedAdmin, setSelectedAdmin] = useState<AdminUser | null>(null);
  const [createLoading, setCreateLoading] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [currentUser, setCurrentUser] = useState<any>(null);

  // 表单状态
  const [createForm, setCreateForm] = useState({ username: '', password: '', role: 'viewer' });
  const [resetForm, setResetForm] = useState({ new_password: '', confirm_password: '' });
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    const user = getUser();
    setCurrentUser(user);
    fetchAdmins();
  }, []);

  const fetchAdmins = async () => {
    try {
      setLoading(true);
      const data = await getAdminList();
      setAdmins(data);
    } catch (error) {
      alert('获取管理员列表失败');
    } finally {
      setLoading(false);
    }
  };

  const validateCreateForm = (): boolean => {
    const errors: { [key: string]: string } = {};

    if (!createForm.username) {
      errors.username = '请输入用户名';
    } else if (createForm.username.length < 3 || createForm.username.length > 20) {
      errors.username = '用户名长度为3-20个字符';
    } else if (!/^[a-zA-Z0-9_]+$/.test(createForm.username)) {
      errors.username = '用户名只能包含字母、数字和下划线';
    }

    if (!createForm.password) {
      errors.password = '请输入密码';
    } else if (createForm.password.length < 6) {
      errors.password = '密码至少6个字符';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateResetForm = (): boolean => {
    const errors: { [key: string]: string } = {};

    if (!resetForm.new_password) {
      errors.new_password = '请输入新密码';
    } else if (resetForm.new_password.length < 6) {
      errors.new_password = '密码至少6个字符';
    }

    if (!resetForm.confirm_password) {
      errors.confirm_password = '请确认新密码';
    } else if (resetForm.new_password !== resetForm.confirm_password) {
      errors.confirm_password = '两次输入的密码不一致';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCreate = async () => {
    if (!validateCreateForm()) return;

    try {
      setCreateLoading(true);
      await createAdmin({
        username: createForm.username,
        password: createForm.password,
        role: createForm.role as 'super' | 'viewer',
      });
      alert('添加成功');
      setCreateModalVisible(false);
      setCreateForm({ username: '', password: '', role: 'viewer' });
      setFormErrors({});
      fetchAdmins();
    } catch (error) {
      alert('添加失败');
    } finally {
      setCreateLoading(false);
    }
  };

  const handleResetPassword = async () => {
    if (!validateResetForm()) return;

    if (!selectedAdmin) return;

    try {
      setResetLoading(true);
      await resetAdminPassword(selectedAdmin.id, { new_password: resetForm.new_password });
      alert('密码重置成功');
      setResetModalVisible(false);
      setResetForm({ new_password: '', confirm_password: '' });
      setFormErrors({});
      setSelectedAdmin(null);
    } catch (error) {
      alert('重置失败');
    } finally {
      setResetLoading(false);
    }
  };

  const openResetModal = (admin: AdminUser) => {
    setSelectedAdmin(admin);
    setResetModalVisible(true);
  };

  const getRoleText = (role: string) => {
    return role === 'super' ? '超级管理员' : '普通管理员';
  };

  const isSuperAdmin = currentUser?.role === 'super';

  return (
    <div className={styles.settings}>
      {/* 工具栏 - 100%按原型 */}
      <div className={styles.toolbar}>
        <div className={styles.toolbarLeft}>
          <h2 className={styles.toolbarTitle}>管理员账号</h2>
        </div>
        <div className={styles.toolbarRight}>
          {isSuperAdmin && (
            <button
              className={styles.addBtn}
              onClick={() => setCreateModalVisible(true)}
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" width="16" height="16">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
              </svg>
              添加管理员
            </button>
          )}
        </div>
      </div>

      {/* 管理员列表 - 100%按原型，放在上面 */}
      <div className={styles.tableCard}>
        {loading ? (
          <div className={styles.loading}>加载中...</div>
        ) : (
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th style={{ width: 80 }}>ID</th>
                  <th>用户名</th>
                  <th style={{ width: 150 }}>角色</th>
                  <th style={{ width: 200 }}>创建时间</th>
                  <th style={{ width: 200 }}>最后登录</th>
                  <th style={{ width: 150 }}>操作</th>
                </tr>
              </thead>
              <tbody>
                {admins.map((admin) => (
                  <tr key={admin.id}>
                    <td className={styles.idCell}>#{admin.id}</td>
                    <td className={styles.nameCell}>{admin.username}</td>
                    <td>
                      <span className={`${styles.roleTag} ${admin.role === 'super' ? styles.roleTagSuper : styles.roleTagViewer}`}>
                        {getRoleText(admin.role)}
                      </span>
                    </td>
                    <td className={styles.dateCell}>
                      {dayjs(admin.created_at).format('YYYY-MM-DD HH:mm')}
                    </td>
                    <td className={styles.dateCell}>
                      {admin.last_login ? dayjs(admin.last_login).format('YYYY-MM-DD HH:mm') : '-'}
                    </td>
                    <td className={styles.actionCell}>
                      {isSuperAdmin && admin.id !== currentUser?.id ? (
                        <button
                          className={styles.resetBtn}
                          onClick={() => openResetModal(admin)}
                        >
                          重置密码
                        </button>
                      ) : (
                        <span className={styles.resetBtnDisabled}>重置密码</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 角色说明 - 100%按原型，放在下面 */}
      <div className={styles.infoCard}>
        <div className={styles.infoTitle}>
          <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          角色权限说明
        </div>
        <div className={styles.infoContent}>
          <div className={styles.roleSection}>
            <div className={styles.roleSectionTitle}>超级管理员</div>
            <ul className={styles.roleList}>
              <li>查看数据看板</li>
              <li>管理用户和日记</li>
              <li>管理系统账号</li>
            </ul>
          </div>
          <div className={styles.roleSection}>
            <div className={styles.roleSectionTitle}>普通管理员</div>
            <ul className={styles.roleList}>
              <li>查看数据看板</li>
              <li>查看用户和日记</li>
              <li>导出数据</li>
            </ul>
          </div>
        </div>
      </div>

      {/* 添加管理员弹窗 */}
      {createModalVisible && (
        <div className={styles.modalOverlay} onClick={() => setCreateModalVisible(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3>添加管理员</h3>
              <button
                className={styles.closeBtn}
                onClick={() => setCreateModalVisible(false)}
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
            <div className={styles.modalBody}>
              <div className={styles.formGroup}>
                <label className={styles.formLabel}>用户名</label>
                <input
                  type="text"
                  className={`${styles.formInput} ${formErrors.username ? styles.formInputError : ''}`}
                  placeholder="请输入用户名"
                  value={createForm.username}
                  onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
                />
                {formErrors.username && <span className={styles.errorText}>{formErrors.username}</span>}
              </div>

              <div className={styles.formGroup}>
                <label className={styles.formLabel}>密码</label>
                <input
                  type="password"
                  className={`${styles.formInput} ${formErrors.password ? styles.formInputError : ''}`}
                  placeholder="请输入密码"
                  value={createForm.password}
                  onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                />
                {formErrors.password && <span className={styles.errorText}>{formErrors.password}</span>}
              </div>

              <div className={styles.formGroup}>
                <label className={styles.formLabel}>角色</label>
                <select
                  className={styles.formSelect}
                  value={createForm.role}
                  onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
                >
                  <option value="viewer">普通管理员</option>
                  <option value="super">超级管理员</option>
                </select>
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button
                className={styles.cancelBtn}
                onClick={() => setCreateModalVisible(false)}
              >
                取消
              </button>
              <button
                className={styles.confirmBtn}
                onClick={handleCreate}
                disabled={createLoading}
              >
                {createLoading ? '添加中...' : '添加'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 重置密码弹窗 */}
      {resetModalVisible && (
        <div className={styles.modalOverlay} onClick={() => setResetModalVisible(false)}>
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3>
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
                </svg>
                重置密码
              </h3>
              <button
                className={styles.closeBtn}
                onClick={() => setResetModalVisible(false)}
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
            <div className={styles.modalBody}>
              <p className={styles.resetHint}>
                正在重置管理员 <strong>{selectedAdmin?.username}</strong> 的密码
              </p>
              <div className={styles.formGroup}>
                <label className={styles.formLabel}>新密码</label>
                <input
                  type="password"
                  className={`${styles.formInput} ${formErrors.new_password ? styles.formInputError : ''}`}
                  placeholder="请输入新密码"
                  value={resetForm.new_password}
                  onChange={(e) => setResetForm({ ...resetForm, new_password: e.target.value })}
                />
                {formErrors.new_password && <span className={styles.errorText}>{formErrors.new_password}</span>}
              </div>

              <div className={styles.formGroup}>
                <label className={styles.formLabel}>确认密码</label>
                <input
                  type="password"
                  className={`${styles.formInput} ${formErrors.confirm_password ? styles.formInputError : ''}`}
                  placeholder="请再次输入新密码"
                  value={resetForm.confirm_password}
                  onChange={(e) => setResetForm({ ...resetForm, confirm_password: e.target.value })}
                />
                {formErrors.confirm_password && <span className={styles.errorText}>{formErrors.confirm_password}</span>}
              </div>
            </div>
            <div className={styles.modalFooter}>
              <button
                className={styles.cancelBtn}
                onClick={() => setResetModalVisible(false)}
              >
                取消
              </button>
              <button
                className={styles.confirmBtn}
                onClick={handleResetPassword}
                disabled={resetLoading}
              >
                {resetLoading ? '重置中...' : '确认重置'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
