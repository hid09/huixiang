/**
 * 首页 - 基于原型设计
 */
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUserStore } from '@/stores/userStore'
import { useRecordStore } from '@/stores/recordStore'
import { diaryApi } from '@/services/api'
import Loading from '@/components/Loading'
import './Home.css'

// 根据时间返回问候语
const getGreeting = () => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  if (hour < 22) return '晚上好'
  return '夜深了'
}

// 根据连续未记录天数返回关怀文案
const getCareMessage = (consecutiveDays: number): string => {
  // 1-3天都用这套轻量关怀文案（随机选择）
  const lightCareMessages = [
    "想说话的时候，我一直在 🌙",
    "今天你安静了一天，也许是想休息一下。",
    "没有记录的日子，也是生活的一部分。",
  ]

  if (consecutiveDays <= 3) {
    return lightCareMessages[Math.floor(Math.random() * lightCareMessages.length)]
  } else if (consecutiveDays <= 7) {
    return "一周没见，有点想念。不过安静也是好的，照顾好自己。"
  } else if (consecutiveDays <= 14) {
    return "好久不见，希望你一切都好。不是催你，只是想打个招呼。"
  } else {
    return "还在这里，随时等你。"
  }
}

// 麦克风图标
const MicIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
  </svg>
)

// 判断内容是否溢出（卡片限制2行，约40字符）
const isContentOverflow = (text: string | null): boolean => {
  if (!text) return false
  // 2行大约40个中文字符（考虑行高和卡片宽度），超过则认为溢出
  return text.length > 40
}

export default function Home() {
  const navigate = useNavigate()
  const { stats, refreshUser, refreshStats } = useUserStore()
  const { todayRecords, isLoading: recordsLoading, fetchTodayRecords } = useRecordStore()
  const [careMessage, setCareMessage] = useState('')

  useEffect(() => {
    console.log('🏠 [首页] 开始加载数据...', new Date().toISOString())
    const startTime = Date.now()

    Promise.all([
      refreshUser().then(() => console.log('✅ refreshUser 完成', Date.now() - startTime, 'ms')),
      refreshStats().then(() => console.log('✅ refreshStats 完成', Date.now() - startTime, 'ms')),
      fetchTodayRecords().then(() => console.log('✅ fetchTodayRecords 完成', Date.now() - startTime, 'ms')),
      fetchConsecutiveEmptyDays().then(() => console.log('✅ fetchConsecutiveEmptyDays 完成', Date.now() - startTime, 'ms'))
    ]).then(() => {
      console.log('🎉 [首页] 所有数据加载完成!', Date.now() - startTime, 'ms')
    })
  }, [refreshUser, refreshStats, fetchTodayRecords])

  // 获取连续未记录天数
  const fetchConsecutiveEmptyDays = async () => {
    try {
      const response = await diaryApi.getConsecutiveEmptyDays()
      if (response.success && response.data) {
        const days = response.data.consecutive_empty_days
        setCareMessage(getCareMessage(days))
      }
    } catch (error) {
      console.error('获取连续未记录天数失败:', error)
      setCareMessage(getCareMessage(1))
    }
  }

  return (
    <div className="home-page">
      {/* 顶部Logo */}
      <header className="home-header">
        <div className="logo">回响<span>·Echo</span></div>
      </header>

      {/* 欢迎区域 */}
      <div className="greeting">
        <div className="greeting-text">{getGreeting()}</div>
        <div className="greeting-sub">
          坚持记录的第 <strong>{stats?.total_record_days || 0}</strong> 天 · 今天想聊点什么？
        </div>
      </div>

      {/* 快捷记录按钮 */}
      <div className="record-btn-container">
        <button className="record-btn" onClick={() => navigate('/record')}>
          <div className="record-icon">
            <MicIcon />
          </div>
          <div className="record-text">
            <div className="record-title">开始记录</div>
            <div className="record-hint">语音或文字，随时记录你的想法</div>
          </div>
        </button>
      </div>

      {/* 今日记录 */}
      <div className="section-header">
        <div className="section-title">今天的记录</div>
      </div>

      {recordsLoading ? (
        <Loading text="加载中..." />
      ) : todayRecords.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-text">
            {careMessage || "想说话的时候，我一直在 🌙"}
          </div>
          <div className="empty-state-author">—— 回响</div>
        </div>
      ) : (
        <div className="record-list">
          {todayRecords.map((record) => {
            const overflow = isContentOverflow(record.transcribed_text)
            return (
              <div
                key={record.id}
                className={`record-item ${overflow ? 'record-item-clickable' : ''}`}
                onClick={() => overflow && navigate(`/record/${record.id}`)}
              >
                <div className="record-item-header">
                  <span className="record-time">
                    {new Date(record.recorded_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  {record.primary_emotion && (
                    <span className="record-emotion">{record.primary_emotion}</span>
                  )}
                </div>
                <div className="record-content">
                  {record.transcribed_text}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
