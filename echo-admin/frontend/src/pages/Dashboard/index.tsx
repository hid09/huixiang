// 数据看板页 - 100%按原型重写
import React, { useEffect, useState } from 'react';
import { Spin } from 'antd';
import ReactECharts from 'echarts-for-react';
import { getDashboardStats } from '@/services/dashboard';
import type { DashboardData } from '@/types/dashboard';
import styles from './Dashboard.module.less';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await getDashboardStats();
      setData(response);
    } catch (error) {
      console.error('获取看板数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  // 7天趋势图配置 - 完全按原型
  const trendOption = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(26, 31, 54, 0.9)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#1a1f36',
        borderWidth: 1,
        padding: 12,
        displayColors: true,
        boxWidth: 8,
        boxHeight: 8,
      }
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: '#6b7280',
          font: { size: 12 },
        }
      },
      y: {
        grid: {
          color: '#f3f4f6',
          borderDash: [5, 5],
        },
        ticks: {
          color: '#6b7280',
          font: { size: 12 },
        }
      }
    },
    interaction: {
      intersect: false,
      mode: 'index',
    }
  };

  // 计算健康度数据
  const failRate = data.ai_health.fail_rate;
  const isSuccessRateSafe = failRate <= 2;
  const healthBarColor = isSuccessRateSafe ? '#4ecdc4' : (failRate <= 5 ? '#feca57' : '#ff6b6b');

  return (
    <div className={styles.dashboard}>
      {/* 概览卡片 - 100%按原型 */}
      <div className={styles.overviewCards}>
        <div className={`${styles.statCard} ${styles.statCard1} ${styles.fadeIn} ${styles.stagger1}`}>
          <div className={styles.statLabel}>
            <svg className={styles.statIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            总用户数
          </div>
          <div className={styles.statValue}>{data.overview.total_users.toLocaleString()}</div>
          <div className={`${styles.statChange} ${styles.statChangeUp}`}>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
              <path d="M6 2L10 7H2L6 2Z"/>
            </svg>
            +12.5% 较上周
          </div>
        </div>

        <div className={`${styles.statCard} ${styles.statCard2} ${styles.fadeIn} ${styles.stagger2}`}>
          <div className={styles.statLabel}>
            <svg className={styles.statIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
            </svg>
            今日 DAU
          </div>
          <div className={styles.statValue} style={{ color: '#ff6b6b' }}>
            {data.overview.dau_today.toLocaleString()}
          </div>
          <div className={`${styles.statChange} ${styles.statChangeUp}`}>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
              <path d="M6 2L10 7H2L6 2Z"/>
            </svg>
            +8.2% 较昨日
          </div>
        </div>

        <div className={`${styles.statCard} ${styles.statCard3} ${styles.fadeIn} ${styles.stagger3}`}>
          <div className={styles.statLabel}>
            <svg className={styles.statIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
            </svg>
            今日录音
          </div>
          <div className={styles.statValue} style={{ color: '#feca57' }}>
            {data.overview.records_today.toLocaleString()}
          </div>
          <div className={`${styles.statChange} ${styles.statChangeUp}`}>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
              <path d="M6 2L10 7H2L6 2Z"/>
            </svg>
            +15.3% 较昨日
          </div>
        </div>

        <div className={`${styles.statCard} ${styles.statCard4} ${styles.fadeIn} ${styles.stagger4}`}>
          <div className={styles.statLabel}>
            <svg className={styles.statIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            今日日记
          </div>
          <div className={styles.statValue} style={{ color: '#a55eea' }}>
            {data.overview.diaries_today.toLocaleString()}
          </div>
          <div className={`${styles.statChange} ${styles.statChangeUp}`}>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
              <path d="M6 2L10 7H2L6 2Z"/>
            </svg>
            +5.9% 较昨日
          </div>
        </div>
      </div>

      {/* AI 健康度 - 100%按原型 */}
      <div className={styles.healthSection}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            AI 生成健康度
          </h2>
        </div>
        <div className={styles.healthCard}>
          <div className={styles.healthItem}>
            <div className={styles.healthLabel}>今日生成成功</div>
            <div className={`${styles.healthValue} ${styles.healthValueSuccess}`}>
              {data.ai_health.success_count}
            </div>
          </div>
          <div className={styles.healthItem}>
            <div className={styles.healthLabel}>今日生成失败</div>
            <div className={`${styles.healthValue} ${styles.healthValueFail}`}>
              {data.ai_health.fail_count}
            </div>
          </div>
          <div className={styles.healthItem}>
            <div className={styles.healthLabel}>失败率</div>
            <div className={`${styles.healthValue} ${styles.healthValueWarning}`}>
              {failRate.toFixed(1)}%
            </div>
          </div>
          <div className={styles.healthBarContainer}>
            <div className={styles.healthBarLabel}>
              失败率进度
              <span className={styles.thresholdTag}>警告阈值: 2%</span>
            </div>
            <div className={styles.healthBar}>
              <div
                className={`${styles.healthBarFill} ${isSuccessRateSafe ? styles.healthBarFillSafe : failRate <= 5 ? styles.healthBarFillWarning : styles.healthBarFillDanger}`}
                style={{ width: `${Math.min(failRate, 100)}%` }}
              ></div>
              <div className={styles.healthBarThreshold}></div>
            </div>
          </div>
        </div>
      </div>

      {/* 7天趋势 - 100%按原型 */}
      <div className={styles.chartSection}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
            </svg>
            7 天趋势
          </h2>
        </div>
        <div className={styles.chartContainer}>
          {data.trend_7d && data.trend_7d.dates && data.trend_7d.dates.length > 0 ? (
            <ReactECharts option={trendOption} style={{ height: 320 }} />
          ) : (
            <div className={styles.emptyChart}>
              <svg width="80" height="80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
              <div className={styles.emptyChartText}>暂无7天趋势数据</div>
            </div>
          )}
        </div>
        {data.trend_7d && data.trend_7d.dates && data.trend_7d.dates.length > 0 && (
          <div className={styles.chartLegend}>
            <div className={styles.legendItem}>
              <div className={styles.legendDot} style={{ background: '#4ecdc4' }}></div>
              新增用户
            </div>
            <div className={styles.legendItem}>
              <div className={styles.legendDot} style={{ background: '#ff6b6b' }}></div>
              活跃用户
            </div>
            <div className={styles.legendItem}>
              <div className={styles.legendDot} style={{ background: '#feca57' }}></div>
              录音数
            </div>
            <div className={styles.legendItem}>
              <div className={styles.legendDot} style={{ background: '#a55eea' }}></div>
              日记数
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
