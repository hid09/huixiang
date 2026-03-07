/**
 * 记录详情页 - 与日记详情页统一风格
 */
import { useParams, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { recordApi, type Record as RecordType } from '@/services/api'
import Loading from '@/components/Loading'
import './RecordDetail.css'

// 返回图标
const BackIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M19 12H5M12 19l-7-7 7-7"/>
  </svg>
)

// 情绪类型映射 - 带渐变色类名
const emotionMap: Record<string, { label: string; className: string }> = {
  positive: { label: '积极', className: 'emotion-positive' },
  negative: { label: '低落', className: 'emotion-negative' },
  neutral: { label: '平静', className: 'emotion-neutral' },
  mixed: { label: '复杂', className: 'emotion-mixed' },
  happy: { label: '开心', className: 'emotion-happy' },
  sad: { label: '难过', className: 'emotion-sad' },
  angry: { label: '愤怒', className: 'emotion-angry' },
  anxious: { label: '焦虑', className: 'emotion-anxious' },
  excited: { label: '兴奋', className: 'emotion-excited' },
  calm: { label: '平静', className: 'emotion-calm' },
}

export default function RecordDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [record, setRecord] = useState<RecordType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchRecord()
  }, [id])

  const fetchRecord = async () => {
    if (!id) return
    setLoading(true)
    setError('')
    try {
      const response = await recordApi.getByIdWithToken(id)
      if (response.success) {
        setRecord(response.data)
      } else {
        setError(response.message || '获取记录失败')
      }
    } catch (err) {
      console.error('获取记录失败:', err)
      setError('记录不存在')
    } finally {
      setLoading(false)
    }
  }

  const formatDateTime = (dateStr: string) => {
    const d = new Date(dateStr)
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return {
      year: d.getFullYear(),
      month: d.getMonth() + 1,
      day: d.getDate(),
      weekday: weekdays[d.getDay()],
      time: d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }
  }

  const getEmotionInfo = (emotion: string | null) => {
    if (!emotion) return null
    return emotionMap[emotion] || { label: emotion, className: 'emotion-neutral' }
  }

  if (loading) {
    return (
      <div className="record-detail-page">
        <div className="record-page-header">
          <button className="back-btn" onClick={() => navigate(-1)}>
            <BackIcon />
          </button>
          <div className="record-page-title">记录详情</div>
        </div>
        <Loading text="加载中..." />
      </div>
    )
  }

  if (error || !record) {
    return (
      <div className="record-detail-page">
        <div className="record-page-header">
          <button className="back-btn" onClick={() => navigate(-1)}>
            <BackIcon />
          </button>
          <div className="record-page-title">记录详情</div>
        </div>
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <div className="empty-text">{error || '记录不存在'}</div>
        </div>
      </div>
    )
  }

  const dateTime = formatDateTime(record.recorded_at)
  const emotionInfo = getEmotionInfo(record.primary_emotion)

  return (
    <div className="record-detail-page">
      {/* 头部导航 */}
      <div className="record-page-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          <BackIcon />
        </button>
        <div className="record-page-title">记录详情</div>
      </div>

      {/* 时间标题区 */}
      <div className="record-detail-header">
        <div className="record-detail-date">
          {dateTime.year}年{dateTime.month}月{dateTime.day}日 · {dateTime.weekday}
        </div>
        <div className="record-detail-time">{dateTime.time}</div>
      </div>

      {/* 情绪标签 */}
      {emotionInfo && (
        <div className="emotion-section">
          <div className={`emotion-badge ${emotionInfo.className}`}>
            {emotionInfo.label}
          </div>
        </div>
      )}

      {/* 记录内容 - 卡片样式 */}
      <div className="diary-section">
        <div className="diary-section-title">
          <span className="diary-section-icon">💬</span>
          我说的话
        </div>
        <div className="diary-section-content">
          <div className="content-text">
            {record.transcribed_text || '无内容'}
          </div>
        </div>

        {/* 元信息 */}
        {record.audio_duration > 0 && (
          <div className="record-detail-meta">
            <span className="meta-label">🎤 录音时长</span>
            <span className="meta-value">
              {Math.floor(record.audio_duration / 60)}:{String(record.audio_duration % 60).padStart(2, '0')}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
