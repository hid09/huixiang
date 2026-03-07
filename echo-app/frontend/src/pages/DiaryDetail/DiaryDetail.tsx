/**
 * 日记详情页（精简版）
 */
import { useParams, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { diaryApi, type Diary } from '@/services/api'
import Loading from '@/components/Loading'
import './DiaryDetail.css'

// 返回图标
const BackIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M19 12H5M12 19l-7-7 7-7"/>
  </svg>
)

// 灯泡图标
const BulbIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 18h6"/>
    <path d="M10 22h4"/>
    <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>
  </svg>
)

export default function DiaryDetail() {
  const { date } = useParams<{ date: string }>()
  const navigate = useNavigate()
  const [diary, setDiary] = useState<Diary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchDiary()
  }, [date])

  const fetchDiary = async () => {
    if (!date) return
    setLoading(true)
    setError('')
    try {
      const response = await diaryApi.getByDate(date)
      if (response.success) {
        setDiary(response.data)
      } else {
        setError(response.message || '获取日记失败')
      }
    } catch (err) {
      console.error('获取日记失败:', err)
      setError('当日暂无日记')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr)
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return {
      year: d.getFullYear(),
      month: d.getMonth() + 1,
      day: d.getDate(),
      weekday: weekdays[d.getDay()]
    }
  }

  if (loading) {
    return (
      <div className="diary-detail-page">
        <div className="record-page-header">
          <button className="back-btn" onClick={() => navigate(-1)}>
            <BackIcon />
          </button>
          <div className="record-page-title">日记详情</div>
        </div>
        <Loading text="加载中..." />
      </div>
    )
  }

  if (error || !diary) {
    return (
      <div className="diary-detail-page">
        <div className="record-page-header">
          <button className="back-btn" onClick={() => navigate(-1)}>
            <BackIcon />
          </button>
          <div className="record-page-title">日记详情</div>
        </div>
        <div className="empty-state">
          <div className="empty-icon">📖</div>
          <div className="empty-text">{error || '日记不存在'}</div>
        </div>
      </div>
    )
  }

  const dateInfo = formatDate(diary.diary_date)

  return (
    <div className="diary-detail-page">
      {/* 头部导航 */}
      <div className="record-page-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          <BackIcon />
        </button>
        <div className="record-page-title">日记详情</div>
      </div>

      {/* 日期标题区 */}
      <div className="diary-detail-header">
        <div className="diary-detail-date">
          {dateInfo.year}年{dateInfo.month}月{dateInfo.day}日 · {dateInfo.weekday} · 第{diary.record_day_count}天
        </div>
        <div className="diary-detail-title">
          {diary.mood_tag || '这一天'}
        </div>
      </div>

      {/* 今天发生了什么 */}
      {diary.what_happened && diary.what_happened.length > 0 && (
        <div className="diary-section">
          <div className="diary-section-title">
            <span className="diary-section-icon">📝</span>
            今天发生了什么
          </div>
          <div className="diary-section-list">
            {diary.what_happened.map((event, i) => (
              <div key={i} className="list-item">• {event}</div>
            ))}
          </div>
        </div>
      )}

      {/* 思考碎片 */}
      {diary.thoughts && diary.thoughts.length > 0 && (
        <div className="diary-section">
          <div className="diary-section-title">
            <span className="diary-section-icon">💭</span>
            思考碎片
          </div>
          <div className="diary-section-list">
            {diary.thoughts.map((thought, i) => (
              <div key={i} className="list-item">• {thought}</div>
            ))}
          </div>
        </div>
      )}

      {/* 小发现 */}
      {diary.small_discovery && (
        <div className="diary-section">
          <div className="diary-section-title">
            <span className="diary-section-icon">🔍</span>
            小发现
          </div>
          <div className="diary-section-content">
            {diary.small_discovery}
          </div>
        </div>
      )}

      {/* 认知小变化 */}
      {diary.cognitive_change && diary.cognitive_change.has_change && (
        <div className="cognitive-card">
          <div className="cognitive-header">
            <BulbIcon />
            认知小变化
          </div>
          {diary.cognitive_change.changes.map((change, i) => (
            <div key={i} className="cognitive-change-item">
              <div className="cognitive-compare">
                <div className="cognitive-item cognitive-old">
                  <div className="cognitive-date">之前</div>
                  <div className="cognitive-text">"{change.before}"</div>
                </div>
                <div className="cognitive-arrow">
                  <svg viewBox="0 0 24 24">
                    <path d="M5 12h14M12 5l7 7-7 7"/>
                  </svg>
                </div>
                <div className="cognitive-item cognitive-new">
                  <div className="cognitive-date">现在</div>
                  <div className="cognitive-text">"{change.after}"</div>
                </div>
              </div>
              {change.topic && (
                <div className="cognitive-topic">关于「{change.topic}」</div>
              )}
            </div>
          ))}
          {diary.cognitive_change.insight && (
            <div className="cognitive-insight">{diary.cognitive_change.insight}</div>
          )}
        </div>
      )}

      {/* 明日提示 */}
      {diary.tomorrow_hint && (
        <div className="diary-section tomorrow-section">
          <div className="diary-section-content">
            🔮 {diary.tomorrow_hint}
          </div>
        </div>
      )}

      {/* 结束语 */}
      {diary.closing && (
        <div className="closing-message">{diary.closing}</div>
      )}
    </div>
  )
}
