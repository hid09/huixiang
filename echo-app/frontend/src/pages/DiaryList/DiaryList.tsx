/**
 * 日记列表页 - 基于原型设计
 * 展示汇总生成的日记（每天一条）
 */
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { diaryApi, type Diary } from '@/services/api'
import Loading from '@/components/Loading'
import './DiaryList.css'

// 搜索图标
const SearchIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="11" cy="11" r="8"></circle>
    <path d="M21 21l-4.35-4.35"></path>
  </svg>
)

// 情绪映射（原型中的情绪类型）
const emotionMap: Record<string, { emoji: string; text: string }> = {
  'positive': { emoji: '😊', text: '开心' },
  'neutral': { emoji: '😌', text: '平静' },
  'negative': { emoji: '😔', text: '低落' },
  'mixed': { emoji: '🤔', text: '复杂' },
  // 兜底映射
  'calm': { emoji: '😌', text: '平静' },
  'happy': { emoji: '😊', text: '开心' },
  'sad': { emoji: '😔', text: '低落' },
  'anxious': { emoji: '😔', text: '焦虑' },
  'tired': { emoji: '😔', text: '疲惫' },
}

const getEmotionInfo = (emotion: string): { emoji: string; text: string } => {
  return emotionMap[emotion] || { emoji: '😌', text: '平静' }
}

export default function DiaryList() {
  const navigate = useNavigate()
  const [diaries, setDiaries] = useState<Diary[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchDiaries()
  }, [])

  const fetchDiaries = async () => {
    setIsLoading(true)
    try {
      const response = await diaryApi.getList()
      if (response.success) {
        setDiaries(response.data.items)
      }
    } catch (error) {
      console.error('获取日记列表失败:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // 格式化日期
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const day = date.getDate()
    const month = date.getMonth() + 1
    const year = date.getFullYear()
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    const weekday = weekdays[date.getDay()]
    return { day, month, year, weekday }
  }

  return (
    <div className="diary-list-page">
      {/* 页面头部 */}
      <header className="page-header">
        <h1>日记</h1>
        <div className="header-actions">
          <button className="icon-btn">
            <SearchIcon />
          </button>
        </div>
      </header>

      {/* 日记列表 */}
      {isLoading ? (
        <Loading text="加载中..." />
      ) : diaries.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📖</div>
          <div className="empty-text">暂无日记</div>
          <div className="empty-hint">每天22:30会自动生成日记哦</div>
        </div>
      ) : (
        <div className="diary-list">
          {diaries.map((diary) => {
            const { day, month, year, weekday } = formatDate(diary.diary_date)
            return (
              <div
                key={diary.id}
                className="diary-card"
                onClick={() => navigate(`/diary/${diary.diary_date}`)}
              >
                <div className="diary-card-header">
                  <div className="diary-date">
                    <div className="diary-date-day">{day}</div>
                    <div className="diary-date-month">{year}年{month}月 · {weekday}</div>
                  </div>
                  <div className="diary-emotion">
                    <span className="diary-emotion-icon">{getEmotionInfo(diary.emotion_type).emoji}</span>
                    <span className="diary-emotion-text">{getEmotionInfo(diary.emotion_type).text}</span>
                  </div>
                </div>
                {diary.what_happened && diary.what_happened.length > 0 && (
                  <div className="diary-preview">
                    {diary.what_happened.join('；')}
                  </div>
                )}
                {diary.keywords && diary.keywords.length > 0 && (
                  <div className="diary-tags">
                    {diary.keywords.slice(0, 3).map((keyword, index) => (
                      <span key={index} className="diary-tag">{keyword}</span>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
