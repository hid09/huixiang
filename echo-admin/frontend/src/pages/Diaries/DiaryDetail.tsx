// 日记详情页 - 完全按原型设计（移除Ant Design）
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';
import { getDiaryDetail } from '@/services/users';
import type { DiaryDetail } from '@/types/user';
import EmotionCompare from '@/components/EmotionCompare';
import styles from './DiaryDetail.module.less';

const DiaryDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [diary, setDiary] = useState<DiaryDetail | null>(null);

  useEffect(() => {
    if (id) {
      fetchDiaryDetail();
    }
  }, [id]);

  const fetchDiaryDetail = async () => {
    try {
      setLoading(true);
      const data = await getDiaryDetail(id!);  // id已经是string类型
      setDiary(data);
    } catch (error: any) {
      console.error('获取日记详情失败:', error);
      alert(`获取日记详情失败: ${error?.response?.data?.detail || error?.message || '未知错误'}`);
    } finally {
      setLoading(false);
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

  const parseJsonArray = (data: string | string[]): string[] => {
    if (Array.isArray(data)) return data;
    try {
      return JSON.parse(data || '[]');
    } catch {
      return [];
    }
  };

  if (loading || !diary) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
      </div>
    );
  }

  const whatHappened = parseJsonArray(diary.what_happened);
  const thoughts = parseJsonArray(diary.thoughts);
  const keywords = parseJsonArray(diary.keywords);

  return (
    <div className={styles.diaryDetail}>
      {/* 页面头部 */}
      <div className={styles.header}>
        <button className={styles.backBtn} onClick={() => navigate(-1)}>
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          返回
        </button>
        <h1 className={styles.pageTitle}>日记详情</h1>
      </div>

      {/* 日记基本信息卡片 */}
      <div className={styles.infoCard}>
        <div className={styles.diaryHeader}>
          <div className={styles.dateInfo}>
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <span className={styles.diaryDate}>{diary.diary_date}</span>
          </div>
          <div className={styles.emotionSection}>
            {diary.emotion_type && (
              <span className={`${styles.emotionTag} ${styles[`emotion${diary.emotion_type.charAt(0).toUpperCase() + diary.emotion_type.slice(1)}`]}`}>
                {getEmotionText(diary.emotion_type)}
              </span>
            )}
            <span className={styles.moodTag}>{diary.mood_tag || '-'}</span>
          </div>
        </div>

        {keywords.length > 0 && (
          <div className={styles.keywordsSection}>
            <span className={styles.sectionLabel}>关键词：</span>
            <div className={styles.keywordsList}>
              {keywords.map((kw, i) => (
                <span key={i} className={styles.keyword}>{kw}</span>
              ))}
            </div>
          </div>
        )}

        <div className={styles.metaInfo}>
          <div className={styles.metaItem}>
            <span className={styles.metaLabel}>用户：</span>
            <button
              className={styles.userLink}
              onClick={() => navigate(`/users/${diary.user.id}`)}
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              {diary.user.username} (ID: {diary.user.id})
            </button>
          </div>
          <div className={styles.metaItem}>
            <span className={styles.metaLabel}>关联录音数：</span>
            <span className={styles.metaValue}>{diary.records_count} 条</span>
          </div>
        </div>

        {/* 情绪分析卡片 */}
        {diary.emotion_type && (
          <div className={styles.emotionCard}>
            <h4 className={styles.cardTitle}>情绪分析</h4>
            <div className={styles.emotionDisplay}>
              <div className={styles.emotionItem}>
                <span className={styles.emotionLabel}>文本情绪</span>
                <span className={`${styles.emotionTag} ${styles[`emotion${diary.emotion_type.charAt(0).toUpperCase() + diary.emotion_type.slice(1)}`]}`}>
                  {getEmotionText(diary.emotion_type)}
                </span>
              </div>
              {diary.records?.[0]?.asr_emotion && (
                <div className={styles.emotionItem}>
                  <span className={styles.emotionLabel}>语音情绪</span>
                  <span className={styles.emotionTagBlue}>{diary.records[0].asr_emotion}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 日记内容 */}
      <div className={styles.contentGrid}>
        {/* 发生了什么 */}
        {whatHappened.length > 0 && (
          <div className={styles.contentCard}>
            <h3 className={styles.cardTitle}>发生了什么</h3>
            <ul className={styles.contentList}>
              {whatHappened.map((item, i) => (
                <li key={i} className={styles.contentItem}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {/* 思考与感悟 */}
        {thoughts.length > 0 && (
          <div className={styles.contentCard}>
            <h3 className={styles.cardTitle}>思考与感悟</h3>
            <ul className={styles.contentList}>
              {thoughts.map((item, i) => (
                <li key={i} className={styles.contentItem}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* 小发现 */}
      {diary.small_discovery && (
        <div className={styles.discoveryCard}>
          <h3 className={styles.cardTitle}>小发现 💡</h3>
          <p className={styles.discoveryText}>{diary.small_discovery}</p>
        </div>
      )}

      {/* 关联的录音记录 */}
      <div className={styles.recordsCard}>
        <h3 className={styles.cardTitle}>关联的录音记录</h3>
        {diary.records && diary.records.length > 0 ? (
          <div className={styles.recordsList}>
            {diary.records.map((record) => (
              <div key={record.id} className={styles.recordItem}>
                <div className={styles.recordHeader}>
                  <span className={styles.recordTime}>
                    {dayjs(record.created_at).format('HH:mm')}
                  </span>
                  <EmotionCompare
                    emotionType={record.emotion_type}
                    asrEmotion={record.asr_emotion}
                    moodTag={record.mood_tag}
                  />
                </div>
                <div className={styles.recordContent}>{record.content}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className={styles.empty}>暂无关联录音记录</div>
        )}
      </div>
    </div>
  );
};

export default DiaryDetail;
