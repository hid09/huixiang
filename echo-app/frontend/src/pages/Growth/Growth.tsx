/**
 * 成长页 - 基于原型设计
 */
import { useState, useEffect } from 'react'
import { useUserStore } from '@/stores/userStore'
import { reviewsApi, type WeeklyReview } from '@/services/api'
import Loading from '@/components/Loading/Loading'
import './Growth.css'

type TabType = 'week' | 'month' | 'quarter' | 'year'

const tabs = [
  { key: 'week' as TabType, label: '周回顾' },
  { key: 'month' as TabType, label: '月度回顾' },
  { key: 'quarter' as TabType, label: '季度总结' },
  { key: 'year' as TabType, label: '年度回顾' },
]

// ========== 月度回顾 Mock 数据（后续实现）==========
const monthlyData = {
  monthName: '二月',
  recordDays: 28,
  voiceCount: 67,
  moodTrend: {
    weeks: [
      { week: '第1周', height: 30, high: false },
      { week: '第2周', height: 45, high: false },
      { week: '第3周', height: 60, high: true },
      { week: '第4周', height: 70, high: true },
    ],
    firstHalf: '波动较多，与工作压力相关',
    secondHalf: '逐渐稳定，"平静"出现频率上升 ↑',
  },
  focusCompare: {
    lastMonth: ['工作', 'deadline', '疲惫'],
    thisMonth: ['读书', '运动', '思考', '家人'],
    insight: '你的注意力从"被动应对"转向"主动生活"',
  },
  habits: [
    { icon: '😴', name: '作息', detail: '23点前入睡从 30% → 70%', status: 'up' },
    { icon: '🏃', name: '运动', detail: '提到跑步 12 次，实际约 8 次', status: 'up' },
    { icon: '📚', name: '学习', detail: '记录中提到读书 15 次', status: 'up' },
    { icon: '👥', name: '社交', detail: '提到"朋友"仅 3 次', status: 'warning' },
  ],
  cognitive: {
    topic: '对"工作"的看法',
    oldView: '"是压力，是负担"',
    newView: '"是挑战，但也有成长"',
    insight: '你在重新定义工作的意义',
  },
  monthlySuggestions: [
    { title: '保持运动节奏', text: '你提到运动时情绪都很积极，这是你的能量来源。建议保持每周 2-3 次的频率。' },
    { title: '适当增加社交', text: '注意到你提到社交的次数不多，但你说过"和朋友聊天后会放松"，可以约个老朋友。' },
    { title: '保持记录节奏', text: '本月记录非常稳定，坚持得很好。下个月继续保持！' },
  ],
}

export default function Growth() {
  const [activeTab, setActiveTab] = useState<TabType>('week')
  const [weeklyData, setWeeklyData] = useState<WeeklyReview | null>(null)
  const [weeklyLoading, setWeeklyLoading] = useState(false)
  const { stats, refreshStats } = useUserStore()

  const hasEnoughData = stats && stats.total_record_days >= 1

  // 页面加载时刷新统计数据
  useEffect(() => {
    refreshStats()
  }, [refreshStats])

  // 获取当前月份名称
  const getCurrentMonthName = () => {
    const months = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']
    return months[new Date().getMonth()]
  }

  // 获取周回顾数据
  useEffect(() => {
    const fetchWeeklyReview = async () => {
      if (activeTab === 'week' && hasEnoughData) {
        setWeeklyLoading(true)
        try {
          const res = await reviewsApi.getWeekly()
          if (res.success && res.data) {
            setWeeklyData(res.data)
          }
        } catch (error) {
          console.error('获取周回顾失败:', error)
        } finally {
          setWeeklyLoading(false)
        }
      }
    }
    fetchWeeklyReview()
  }, [activeTab, hasEnoughData])

  return (
    <div className="growth-page">
      {/* 页面头部 */}
      <header className="page-header">
        <h1>成长</h1>
      </header>

      {/* 标签切换 */}
      <div className="review-tabs">
        {tabs.map((tab) => (
          <div
            key={tab.key}
            className={`review-tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </div>
        ))}
      </div>

      {/* 季度/年度总结 - MVP后迭代 */}
      {(activeTab === 'quarter' || activeTab === 'year') && (
        <div className="empty-state">
          <div className="empty-icon">📈</div>
          <div className="empty-text">敬请期待</div>
          <div className="empty-hint">该功能正在开发中，敬请期待</div>
        </div>
      )}

      {/* 周回顾 */}
      {activeTab === 'week' && (
        <>
          {!hasEnoughData ? (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <div className="empty-text">暂无复盘</div>
              <div className="empty-hint">坚持记录一段时间后，这里会有精彩的分析</div>
            </div>
          ) : weeklyLoading ? (
            <Loading text="正在生成周回顾..." />
          ) : (
            <>
              {/* 统计概览 */}
              <div className="review-stats">
                <div className="review-stat-item">
                  <div className="review-stat-value">{weeklyData?.record_days || 0}</div>
                  <div className="review-stat-label">记录天数</div>
                </div>
                <div className="review-stat-item">
                  <div className="review-stat-value">{weeklyData?.voice_count || 0}</div>
                  <div className="review-stat-label">语音条数</div>
                </div>
                <div className="review-stat-item">
                  <div className="review-stat-value">{weeklyData?.dominant_emotion || '😌'}</div>
                  <div className="review-stat-label">主导情绪</div>
                </div>
              </div>

              {/* 情绪日历 */}
              <div className="review-chart">
                <div className="review-chart-title">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                    <line x1="9" y1="9" x2="9.01" y2="9"/>
                    <line x1="15" y1="9" x2="15.01" y2="9"/>
                  </svg>
                  本周情绪
                </div>
                <div className="mood-calendar">
                  <div className="mood-calendar-row">
                    {weeklyData?.emotion_trend?.map((item, index) => (
                      <div key={index} className="mood-day">
                        <div className={`mood-circle mood-${item.emotion_type === 'positive' ? 'happy' : item.emotion_type === 'negative' ? 'sad' : 'calm'}`}>
                          {item.emoji}
                        </div>
                        <span className="mood-label">{item.day}</span>
                      </div>
                    ))}
                  </div>
                  <div className="mood-legend">
                    <div className="mood-legend-item">
                      <span className="mood-legend-dot calm"></span>
                      <span>平静</span>
                    </div>
                    <div className="mood-legend-item">
                      <span className="mood-legend-dot happy"></span>
                      <span>开心</span>
                    </div>
                    <div className="mood-legend-item">
                      <span className="mood-legend-dot sad"></span>
                      <span>低落</span>
                    </div>
                  </div>
                  <div className="mood-summary">
                    <span>积极情绪</span>
                    <div className="mood-bar">
                      <div className="mood-bar-fill" style={{ width: `${weeklyData?.positive_ratio || 0}%` }}></div>
                    </div>
                    <span className="mood-positive"><strong>{weeklyData?.positive_ratio || 0}%</strong></span>
                  </div>
                </div>
              </div>

              {/* 关键词云 */}
              <div className="review-chart-title" style={{ marginBottom: 12 }}>
                🏷 本周关键词
              </div>
              <div className="keywords-cloud">
                {weeklyData?.keywords?.map((keyword, index) => (
                  <span
                    key={index}
                    className={`keyword-tag ${keyword.large ? 'large' : ''}`}
                  >
                    {keyword.text}
                  </span>
                ))}
              </div>

              {/* 建议区块 */}
              <div className="suggestion-section">
                <div className="suggestion-title">💡 给你的建议</div>
                <div className="suggestion-list">
                  {weeklyData?.suggestions?.map((item, index) => (
                    <div key={index} className="suggestion-item">{item}</div>
                  ))}
                </div>
              </div>
            </>
          )}
        </>
      )}

      {/* 月度回顾 */}
      {activeTab === 'month' && (
        <>
          {/* 月度概览卡片 */}
          <div className="monthly-overview">
            <div className="monthly-overview-title">{monthlyData.monthName}回顾</div>
            <div className="monthly-stats-row">
              <div className="monthly-stat">
                <div className="monthly-stat-value">{monthlyData.recordDays}<span className="monthly-stat-unit">天</span></div>
                <div className="monthly-stat-label">共记录</div>
              </div>
              <div className="monthly-stat">
                <div className="monthly-stat-value">{monthlyData.voiceCount}<span className="monthly-stat-unit">条</span></div>
                <div className="monthly-stat-label">语音记录</div>
              </div>
            </div>
          </div>

          {/* 情绪状态变化 */}
          <div className="mood-trend-section">
            <div className="mood-trend-title">📈 情绪状态变化</div>
            <div className="mood-trend-chart">
              {monthlyData.moodTrend.weeks.map((item, index) => (
                <div key={index} className="mood-bar-item">
                  <div className={`mood-bar-visual ${item.high ? 'high' : ''}`} style={{ height: item.height }}></div>
                  <span className="mood-bar-label">{item.week}</span>
                </div>
              ))}
            </div>
            <div className="mood-trend-summary">
              <div className="mood-trend-half">
                <strong>上半月：</strong>{monthlyData.moodTrend.firstHalf}
              </div>
              <div className="mood-trend-half">
                <strong>下半月：</strong>{monthlyData.moodTrend.secondHalf}
              </div>
            </div>
          </div>

          {/* 关注点变化 */}
          <div className="focus-compare-section">
            <div className="focus-compare-title">🏷️ 关注点变化</div>
            <div className="focus-compare-row">
              <div className="focus-month">
                <div className="focus-month-label">一月高频词</div>
                <div className="focus-tags">
                  {monthlyData.focusCompare.lastMonth.map((tag, i) => (
                    <span key={i} className="focus-tag old">{tag}</span>
                  ))}
                </div>
              </div>
              <div className="focus-month">
                <div className="focus-month-label">二月高频词</div>
                <div className="focus-tags">
                  {monthlyData.focusCompare.thisMonth.map((tag, i) => (
                    <span key={i} className="focus-tag new">{tag}</span>
                  ))}
                </div>
              </div>
            </div>
            <div className="focus-insight">{monthlyData.focusCompare.insight}</div>
          </div>

          {/* 行为习惯变化 */}
          <div className="habit-section">
            <div className="habit-title">✅ 行为习惯变化</div>
            <div className="habit-list">
              {monthlyData.habits.map((habit, index) => (
                <div key={index} className="habit-item">
                  <span className="habit-icon">{habit.icon}</span>
                  <div className="habit-info">
                    <div className="habit-name">{habit.name}</div>
                    <div className="habit-detail">{habit.detail}</div>
                  </div>
                  <span className={`habit-status ${habit.status}`}>
                    {habit.status === 'up' ? '↑' : '⚠'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* 认知/观点变化 */}
          <div className="cognitive-monthly-section">
            <div className="cognitive-monthly-title">💡 认知/观点变化</div>
            <div className="cognitive-monthly-topic">{monthlyData.cognitive.topic}</div>
            <div className="cognitive-monthly-compare">
              <div className="cognitive-monthly-item old">
                <div className="cognitive-monthly-label">一月</div>
                <div className="cognitive-monthly-text">{monthlyData.cognitive.oldView}</div>
              </div>
              <div className="cognitive-monthly-arrow">
                <svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </div>
              <div className="cognitive-monthly-item new">
                <div className="cognitive-monthly-label">二月</div>
                <div className="cognitive-monthly-text">{monthlyData.cognitive.newView}</div>
              </div>
            </div>
            <div className="cognitive-monthly-insight">{monthlyData.cognitive.insight}</div>
          </div>

          {/* 月度建议 */}
          <div className="monthly-suggestion-section">
            <div className="monthly-suggestion-title">💌 给你的{getCurrentMonthName()}建议</div>
            <div className="monthly-suggestion-list">
              {monthlyData.monthlySuggestions.map((item, index) => (
                <div key={index} className="monthly-suggestion-item">
                  <div className="monthly-suggestion-head">
                    <span className="monthly-suggestion-num">{index + 1}</span>{item.title}
                  </div>
                  <div className="monthly-suggestion-text">{item.text}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
