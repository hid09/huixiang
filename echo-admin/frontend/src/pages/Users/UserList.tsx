// 用户列表页 - 完全按原型设计（移除Ant Design）
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { getUserList, exportUsers, resetUserPassword } from '@/services/users';
import type { UserListItem, UserListParams } from '@/types/user';
import styles from './UserList.module.less';

const UserList: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [resetting, setResetting] = useState<string | null>(null);  // 正在重置的用户ID
  const [data, setData] = useState<UserListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [params, setParams] = useState<UserListParams>({
    page: 1,
    page_size: 20,
    keyword: '',
    start_date: '',
    end_date: '',
  });
  const [searchKeyword, setSearchKeyword] = useState('');

  useEffect(() => {
    fetchData();
  }, [params]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await getUserList(params);
      setData(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('获取用户列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setParams({ ...params, keyword: searchKeyword, page: 1 });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleDateRangeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // 简化版本：直接用输入框，实际可用第三方日期选择器库
    const value = e.target.value;
    // TODO: 实现日期范围筛选功能
    setParams({ ...params, start_date: value, page: 1 });
  };

  const handleExport = async () => {
    try {
      setExporting(true);
      const blob = await exportUsers();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `用户列表_${dayjs().format('YYYYMMDD_HHmmss')}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
      alert('导出成功');
    } catch (error) {
      alert('导出失败');
    } finally {
      setExporting(false);
    }
  };

  const handlePageChange = (page: number) => {
    setParams({ ...params, page });
  };

  const handleResetPassword = async (userId: string, userName: string) => {
    // 二次确认
    const confirmed = window.confirm(`确定要将用户「${userName}」的密码重置为默认密码「huixiang」吗？`);
    if (!confirmed) return;

    try {
      setResetting(userId);
      await resetUserPassword(userId);
      alert(`密码已重置成功！新密码：huixiang`);
    } catch (error: any) {
      alert(`重置失败：${error?.response?.data?.message || error?.message || '未知错误'}`);
    } finally {
      setResetting(null);
    }
  };

  return (
    <div className={styles.userList}>
      {/* 搜索区域 */}
      <div className={styles.searchCard}>
        <div className={styles.searchRow}>
          <div className={styles.searchLeft}>
            <div className={styles.searchInput}>
              <svg className={styles.searchIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              <input
                type="text"
                placeholder="搜索用户名或手机号"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                onKeyPress={handleKeyPress}
              />
              <button className={styles.searchBtn} onClick={handleSearch}>
                搜索
              </button>
            </div>
            <input
              type="date"
              className={styles.dateInput}
              onChange={handleDateRangeChange}
            />
            <button className={styles.refreshBtn} onClick={fetchData}>
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              刷新
            </button>
          </div>
          <button
            className={`${styles.exportBtn} ${exporting ? styles.exportBtnLoading : ''}`}
            onClick={handleExport}
            disabled={exporting}
          >
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            {exporting ? '导出中...' : '导出'}
          </button>
        </div>
      </div>

      {/* 数据表格 */}
      <div className={styles.tableCard}>
        {loading ? (
          <div className={styles.loading}>
            <div className={styles.spinner}></div>
            <div className={styles.loadingText}>加载中...</div>
          </div>
        ) : data.length === 0 ? (
          <div className={styles.empty}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
            </svg>
            <div className={styles.emptyText}>暂无数据</div>
          </div>
        ) : (
          <>
            <div className={styles.tableWrapper}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th style={{ width: 100 }}>用户ID</th>
                    <th style={{ width: 140 }}>用户名</th>
                    <th style={{ width: 160 }}>注册时间</th>
                    <th style={{ width: 100, textAlign: 'center' }}>录音数</th>
                    <th style={{ width: 100, textAlign: 'center' }}>日记数</th>
                    <th style={{ width: 160 }}>最后活跃</th>
                    <th style={{ width: 140, textAlign: 'center' }}>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((user) => (
                    <tr key={user.id}>
                      <td className={styles.idCell}>{user.id.slice(0, 8)}</td>
                      <td className={styles.nameCell}>
                        {user.name || user.username}
                      </td>
                      <td className={styles.dateCell}>
                        {dayjs(user.created_at).format('YYYY-MM-DD HH:mm')}
                      </td>
                      <td className={styles.countCell}>
                        <span className={styles.tagPurple}>{user.records_count}</span>
                      </td>
                      <td className={styles.countCell}>
                        <span className={styles.tagOrange}>{user.diaries_count}</span>
                      </td>
                      <td className={styles.dateCell}>
                        {user.last_active ? dayjs(user.last_active).format('YYYY-MM-DD HH:mm') : '-'}
                      </td>
                      <td className={styles.actionCell}>
                        <button
                          className={styles.detailBtn}
                          onClick={() => navigate(`/users/${user.id}`)}
                        >
                          查看
                        </button>
                        <button
                          className={styles.resetBtn}
                          onClick={() => handleResetPassword(user.id, user.name || user.username)}
                          disabled={resetting === user.id}
                        >
                          {resetting === user.id ? '重置中' : '重置'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* 分页器 */}
            <div className={styles.pagination}>
              <div className={styles.paginationInfo}>
                共 {total} 条数据
              </div>
              <div className={styles.paginationControls}>
                <button
                  className={styles.pageBtn}
                  onClick={() => handlePageChange(params.page - 1)}
                  disabled={params.page === 1}
                >
                  上一页
                </button>
                <div className={styles.pageNumbers}>
                  {params.page}
                </div>
                <button
                  className={styles.pageBtn}
                  onClick={() => handlePageChange(params.page + 1)}
                  disabled={params.page * params.page_size >= total}
                >
                  下一页
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default UserList;
