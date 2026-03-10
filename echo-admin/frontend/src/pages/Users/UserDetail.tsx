// 用户详情页 - 完全按原型设计
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { getUserDetail, getUserRecords, getUserDiaries } from '@/services/users';
import type { UserDetail, RecordItem, DiaryItem } from '@/types/user';
import styles from './UserDetail.module.less';

const UserDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<UserDetail | null>(null);
  const [activeTab, setActiveTab] = useState<'records' | 'diaries'>('records');
  const [recordsLoading, setRecordsLoading] = useState(false);
  const [diariesLoading, setDiariesLoading] = useState(false);
  const [records, setRecords] = useState<RecordItem[]>([]);
  const [recordsTotal, setRecordsTotal] = useState(0);
  const [diaries, setDiaries] = useState<DiaryItem[]>([]);
  const [diariesTotal, setDiariesTotal] = useState(0);
  const [recordsPage, setRecordsPage] = useState(1);
  const [diariesPage, setDiariesPage] = useState(1);

  useEffect(() => {
    if (id) {
      fetchUserDetail();
      fetchRecords();
      fetchDiaries();
    }
  }, [id]);

  const fetchUserDetail = async () => {
    try {
      setLoading(true);
      const data = await getUserDetail(id!);  // id已经是string类型
      setUser(data);
    } catch (error: any) {
      console.error('获取用户详情失败:', error);
      alert(`获取用户详情失败: ${error?.response?.data?.detail || error?.message || '未知错误'}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecords = async (page = 1) => {
    try {
      setRecordsLoading(true);
      const response = await getUserRecords(id!, { page, page_size: 10 });
      setRecords(response.items);
      setRecordsTotal(response.total);
      setRecordsPage(page);
    } catch (error: any) {
      console.error('获取录音记录失败:', error);
      alert(`获取录音记录失败: ${error?.response?.data?.detail || error?.message || '未知错误'}`);
    } finally {
      setRecordsLoading(false);
    }
  };

  const fetchDiaries = async (page = 1) => {
    try {
      setDiariesLoading(true);
      const response = await getUserDiaries(id!, { page, page_size: 10 });
      setDiaries(response.items);
      setDiariesTotal(response.total);
      setDiariesPage(page);
    } catch (error: any) {
      console.error('获取日记记录失败:', error);
      alert(`获取日记记录失败: ${error?.response?.data?.detail || error?.message || '未知错误'}`);
    } finally {
      setDiariesLoading(false);
    }
  };

  const getEmotionText = (type: string) => {
    const texts: Record<string, string> = {
      positive: '积极',
      neutral: '平静',
      negative: '消极',
      mixed: '复杂',
    };
    return texts[type] || type;
  };

  // 获取情绪类型对应的颜色样式
  const getEmotionColorClass = (emotion: string) => {
    // 支持中文和英文
    const positiveTypes = ['positive', '开心', '积极', 'happy'];
    const neutralTypes = ['neutral', '平静', '困惑'];
    const negativeTypes = ['negative', '消极', '疲惫', '焦虑', '烦躁', 'sad', 'angry'];

    if (positiveTypes.includes(emotion)) return styles.tagTeal;
    if (negativeTypes.includes(emotion)) return styles.tagCoral;
    if (neutralTypes.includes(emotion)) return styles.tagAmber;
    return styles.tagGray;
  };

  // 获取ASR情绪颜色
  const getAsrEmotionColor = (asr: string) => {
    if (asr === 'happy') return styles.tagTeal;
    if (asr === 'sad') return styles.tagAmber;
    if (asr === 'angry') return styles.tagCoral;
    if (asr === 'neutral') return styles.tagTeal;
    return styles.tagGray;
  };

  if (loading || !user) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
      </div>
    );
  }

  return (
    <div className={styles.userDetail}>
      {/* 基本信息卡片 */}
      <div className={styles.infoCard}>
        <div className={styles.infoCardTitle}>
          <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
          </svg>
          基本信息
        </div>
        <div className={styles.infoGrid}>
          <div className={styles.infoItem}>
            <div className={styles.infoLabel}>用户ID</div>
            <div className={styles.infoValue} title={user.id}>{user.id.slice(0, 8)}...</div>
          </div>
          <div className={styles.infoItem}>
            <div className={styles.infoLabel}>用户名</div>
            <div className={styles.infoValue}>{user.name || user.username}</div>
          </div>
          <div className={styles.infoItem}>
            <div className={styles.infoLabel}>注册时间</div>
            <div className={styles.infoValue}>{dayjs(user.created_at).format('YYYY-MM-DD HH:mm')}</div>
          </div>
          <div className={styles.infoItem}>
            <div className={styles.infoLabel}>连续打卡</div>
            <div className={styles.infoValue}>{user.continuous_days || 0} 天</div>
          </div>
          <div className={styles.infoItem}>
            <div className={styles.infoLabel}>累计录音</div>
            <div className={styles.infoValue} style={{color: '#4ecdc4'}}>{user.total_voice_count || user.records_count || 0} 条</div>
          </div>
          <div className={styles.infoItem}>
            <div className={styles.infoLabel}>累计日记</div>
            <div className={styles.infoValue} style={{color: '#a55eea'}}>{user.diaries_count || 0} 篇</div>
          </div>
          <div className={styles.infoItem}>
            <div className={styles.infoLabel}>最近活跃</div>
            <div className={styles.infoValue}>
              {user.last_active ? dayjs(user.last_active).format('YYYY-MM-DD HH:mm') : '-'}
            </div>
          </div>
          <div className={styles.infoItem}>
            <div className={styles.infoLabel}>使用天数</div>
            <div className={styles.infoValue}>{user.days_active} 天</div>
          </div>
        </div>
      </div>

      {/* Tab 切换 - 100%按原型 */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'records' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('records')}
        >
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{verticalAlign: 'middle', marginRight: '6px'}}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
          </svg>
          录音记录
        </button>
        <button
          className={`${styles.tab} ${activeTab === 'diaries' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('diaries')}
        >
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{verticalAlign: 'middle', marginRight: '6px'}}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
          </svg>
          日记记录
        </button>
      </div>

      {/* Tab 内容 */}
      <div className={styles.tabContent}>
        {activeTab === 'records' && (
          recordsLoading ? (
            <div className={styles.loading}>加载中...</div>
          ) : records.length === 0 ? (
            <div className={styles.empty}>暂无录音记录</div>
          ) : (
            <>
              {/* 录音记录表格 - 100%按原型 */}
              <div className={styles.recordTableCard}>
                <table className={styles.recordTable}>
                  <thead>
                    <tr>
                      <th style={{width: 150}}>录音时间</th>
                      <th style={{width: 280}}>内容摘要</th>
                      <th style={{width: 90}}>ASR情绪</th>
                      <th style={{width: 90}}>文本情绪</th>
                      <th style={{width: 90}}>心情标签</th>
                      <th style={{width: 100, textAlign: 'center'}}>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((record) => (
                      <tr key={record.id}>
                        <td className={styles.recordTime}>
                          {dayjs(record.created_at).format('YYYY-MM-DD HH:mm')}
                        </td>
                        <td className={styles.recordContent}>
                          {record.content?.slice(0, 50)}
                          {record.content && record.content.length > 50 ? '...' : ''}
                        </td>
                        <td className={styles.recordTagCell}>
                          <span className={`${styles.tag} ${getAsrEmotionColor(record.asr_emotion || '')}`}>
                            {record.asr_emotion || '-'}
                          </span>
                        </td>
                        <td className={styles.recordTagCell}>
                          <span className={`${styles.tag} ${getEmotionColorClass(record.emotion_type || '')}`}>
                            {record.emotion_type || '-'}
                          </span>
                        </td>
                        <td className={styles.recordTagCell}>
                          <span className={`${styles.tag} ${getEmotionColorClass(record.mood_tag || '')}`}>
                            {record.mood_tag || '-'}
                          </span>
                        </td>
                        <td style={{textAlign: 'center'}}>
                          <button className={styles.detailBtn}>查看</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div className={styles.pagination}>
                  <div className={styles.paginationInfo}>
                    共 {recordsTotal} 条录音，当前显示 {(recordsPage - 1) * 10 + 1}-{Math.min(recordsPage * 10, recordsTotal)} 条
                  </div>
                  <div className={styles.paginationBtns}>
                    <button
                      className={styles.pageBtn}
                      onClick={() => fetchRecords(recordsPage - 1)}
                      disabled={recordsPage === 1}
                    >
                      &lt;
                    </button>
                    <button
                      className={styles.pageBtn}
                      onClick={() => fetchRecords(1)}
                    >
                      {recordsPage}
                    </button>
                    <button
                      className={styles.pageBtn}
                      onClick={() => fetchRecords(Math.min(recordsPage + 1, Math.ceil(recordsTotal / 10)))}
                    >
                      &gt;
                    </button>
                  </div>
                </div>
              </div>
            </>
          )
        )}

        {activeTab === 'diaries' && (
          diariesLoading ? (
            <div className={styles.loading}>加载中...</div>
          ) : diaries.length === 0 ? (
            <div className={styles.empty}>暂无日记记录</div>
          ) : (
            <>
              {/* 日记记录列表 - 卡片形式 */}
              <div className={styles.diaryListSimple}>
                {diaries.map((diary) => (
                  <div
                    key={diary.id}
                    className={styles.diaryItem}
                    onClick={() => navigate(`/diaries/${diary.id}`)}
                  >
                    <div className={styles.diaryItemHeader}>
                      <div className={styles.diaryItemDate}>{diary.diary_date}</div>
                      <div className={styles.diaryItemTags}>
                        {diary.emotion_type && (
                          <span className={`${styles.tag} ${getEmotionColorClass(diary.emotion_type || '')}`}>
                            {diary.emotion_type}
                          </span>
                        )}
                        {diary.mood_tag && (
                          <span className={`${styles.tag} ${getEmotionColorClass(diary.mood_tag || '')}`}>
                            {diary.mood_tag}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className={styles.diaryItemPreview}>
                      {(() => {
                        try {
                          const arr = typeof diary.what_happened === 'string'
                            ? JSON.parse(diary.what_happened)
                            : diary.what_happened;
                          const content = Array.isArray(arr) ? arr.join('，') : diary.what_happened;
                          return content ? content.slice(0, 100) + (content.length > 100 ? '...' : '') : '-';
                        } catch {
                          return diary.what_happened || '-';
                        }
                      })()}
                    </div>
                    <div className={styles.diaryItemFooter}>
                      <div className={styles.diaryItemMeta}>
                        {diary.records_count} 条录音 · 关键词：
                        {(() => {
                          const kw = diary.keywords;
                          let keywordsList: string[] = [];
                          if (Array.isArray(kw)) {
                            keywordsList = kw;
                          } else if (typeof kw === 'string' && kw) {
                            try {
                              const parsed = JSON.parse(kw);
                              keywordsList = Array.isArray(parsed) ? parsed : [];
                            } catch {
                              keywordsList = [];
                            }
                          }
                          return keywordsList.slice(0, 2).join('、');
                        })()}
                      </div>
                      <div className={styles.btnText}>查看详情 →</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* 分页 */}
              {diariesTotal > 10 && (
                <div className={styles.pagination}>
                  <div className={styles.paginationInfo}>
                    共 {diariesTotal} 篇日记，当前显示 {(diariesPage - 1) * 10 + 1}-{Math.min(diariesPage * 10, diariesTotal)} 篇
                  </div>
                  <div className={styles.paginationBtns}>
                    <button
                      className={styles.pageBtn}
                      onClick={() => fetchDiaries(diariesPage - 1)}
                      disabled={diariesPage === 1}
                    >
                      &lt;
                    </button>
                    <button
                      className={styles.pageBtn}
                      onClick={() => fetchDiaries(1)}
                    >
                      {diariesPage}
                    </button>
                    <button
                      className={styles.pageBtn}
                      onClick={() => fetchDiaries(Math.min(diariesPage + 1, Math.ceil(diariesTotal / 10)))}
                    >
                      &gt;
                    </button>
                  </div>
                </div>
              )}
            </>
          )
        )}
      </div>
    </div>
  );
};

export default UserDetail;
