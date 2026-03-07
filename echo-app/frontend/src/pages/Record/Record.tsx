/**
 * 记录页 - 基于原型设计
 * 支持语音录制和文字输入
 */
import { useState, useCallback, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Toast } from 'antd-mobile'
import { useRecordStore } from '@/stores/recordStore'
import { recordApi } from '@/services/api'
import AudioRecorder from '@/components/AudioRecorder'
import './Record.css'

// 编辑图标
const EditIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
  </svg>
)

// 返回图标
const BackIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M19 12H5M12 19l-7-7 7-7"/>
  </svg>
)

// 加载图标
const LoadingIcon = () => (
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 6v6l4 2"/>
  </svg>
)

// 获取时间问候
const getRecordGreeting = () => {
  const now = new Date()
  const month = now.getMonth() + 1
  const day = now.getDate()
  const hour = now.getHours()

  let timeGreeting = ''
  if (hour < 6) timeGreeting = '夜深了'
  else if (hour < 9) timeGreeting = '早上好'
  else if (hour < 12) timeGreeting = '上午好'
  else if (hour < 14) timeGreeting = '中午好'
  else if (hour < 18) timeGreeting = '下午好'
  else if (hour < 22) timeGreeting = '晚上好'
  else timeGreeting = '夜深了'

  return `${month}月${day}日 · ${timeGreeting}`
}

// 录音状态类型
type RecordState = 'idle' | 'recorded' | 'transcribing' | 'success'

export default function Record() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const isTextMode = searchParams.get('type') === 'text'

  const [text, setText] = useState('')
  const [showTextInput, setShowTextInput] = useState(isTextMode)
  const [recordState, setRecordState] = useState<RecordState>('idle')
  const [transcribedText, setTranscribedText] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [isVoiceSubmitting, setIsVoiceSubmitting] = useState(false)

  // 保存录音数据（用于确认发送时上传）
  const audioBlobRef = useRef<Blob | null>(null)
  const audioDurationRef = useRef<number>(0)

  const { submitTextRecord, isSubmitting } = useRecordStore()

  // 录音完成回调 - 只转写，不保存
  const handleRecordComplete = useCallback(async (blob: Blob, duration: number) => {
    console.log('录音完成:', duration, '秒')
    setRecordState('transcribing')

    // 保存录音数据
    audioBlobRef.current = blob
    audioDurationRef.current = duration

    try {
      // 只调用转写接口，不保存记录
      const response = await recordApi.transcribeVoice(blob)

      if (response.success && response.data) {
        setTranscribedText(response.data.text || '')
        setIsEditing(false)
        setRecordState('success')
        console.log('语音转写成功:', response.data.text)
      } else {
        Toast.show({ content: response.message || '转写失败，请重试', icon: 'fail' })
        setRecordState('idle')
      }
    } catch (error) {
      console.error('语音转写失败:', error)
      Toast.show({ content: '转写失败，请检查网络', icon: 'fail' })
      setRecordState('idle')
    }
  }, [])

  // 确认发送 - 保存记录（会对编辑后的文本做情绪分析）
  const handleConfirmSend = async () => {
    if (!transcribedText.trim()) {
      Toast.show({ content: '内容不能为空', icon: 'fail' })
      return
    }

    try {
      setIsVoiceSubmitting(true)
      // 获取本地日期
      const now = new Date()
      let localDate: string
      if (now.getHours() < 6) {
        const yesterday = new Date(now)
        yesterday.setDate(yesterday.getDate() - 1)
        localDate = yesterday.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        }).replace(/\//g, '-')
      } else {
        localDate = now.toLocaleDateString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        }).replace(/\//g, '-')
      }

      // 使用新接口：对编辑后的文本做情绪分析并保存
      const response = await recordApi.confirmVoiceRecord(transcribedText, localDate)

      if (response.success) {
        Toast.show({ content: '记录成功！', icon: 'success' })
        // 清理数据
        audioBlobRef.current = null
        audioDurationRef.current = 0
        // 首页会自己刷新，不需要在这里调用
        setTimeout(() => {
          navigate('/')
        }, 300)
      } else {
        Toast.show({ content: response.message || '记录失败，请重试', icon: 'fail' })
      }
    } catch (error) {
      console.error('保存记录失败:', error)
      Toast.show({ content: '记录失败，请检查网络', icon: 'fail' })
    } finally {
      setIsVoiceSubmitting(false)
    }
  }

  // 重新录制 - 丢弃数据，返回录音页面
  const handleRerecord = () => {
    // 清理所有数据
    setTranscribedText('')
    setIsEditing(false)
    audioBlobRef.current = null
    audioDurationRef.current = 0
    setRecordState('idle')
  }

  // 提交文字
  const handleSubmitText = async () => {
    if (!text.trim()) {
      Toast.show({ content: '请输入内容', icon: 'fail' })
      return
    }

    const success = await submitTextRecord(text)
    if (success) {
      Toast.show({ content: '记录成功！', icon: 'success' })
      setText('')
      navigate('/')
    } else {
      Toast.show({ content: '记录失败，请重试', icon: 'fail' })
    }
  }

  // 文字模式
  if (isTextMode || showTextInput) {
    return (
      <div className="record-page">
        <div className="record-page-header">
          <button className="back-btn" onClick={() => navigate(-1)}>
            <BackIcon />
          </button>
          <div className="record-page-title">文字记录</div>
        </div>

        <div className="text-mode-section">
          <div className="input-area">
            <div className="input-label">写下你的想法</div>
            <textarea
              className="text-input"
              placeholder="今天过得怎么样？有什么想说的..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              maxLength={500}
            />
          </div>
          <button
            className="submit-btn"
            onClick={handleSubmitText}
            disabled={!text.trim() || isSubmitting}
          >
            {isSubmitting ? '发送中...' : '发送'}
          </button>
        </div>
      </div>
    )
  }

  // 转写中状态
  if (recordState === 'transcribing') {
    return (
      <div className="record-page">
        <div className="record-page-header">
          <button className="back-btn" onClick={() => navigate(-1)}>
            <BackIcon />
          </button>
          <div className="record-page-title">转写中</div>
        </div>

        <div className="transcribing-state">
          <div className="transcribing-icon">
            <LoadingIcon />
          </div>
          <div className="transcribing-text">正在将语音转为文字...</div>
        </div>
      </div>
    )
  }

  // 转写成功状态（可编辑）
  if (recordState === 'success' && transcribedText) {
    return (
      <div className="record-page">
        <div className="record-page-header">
          <button className="back-btn" onClick={() => navigate(-1)}>
            <BackIcon />
          </button>
          <div className="record-page-title">转写结果</div>
        </div>

        <div className="transcribe-result">
          <div className="transcribe-result-header">
            <div className="transcribe-result-label">语音转写</div>
            {!isEditing && (
              <button className="btn-edit" onClick={() => setIsEditing(true)}>
                编辑
              </button>
            )}
          </div>

          {isEditing ? (
            <textarea
              className="transcribe-edit-textarea"
              value={transcribedText}
              onChange={(e) => setTranscribedText(e.target.value)}
              placeholder="编辑转写内容..."
              autoFocus
            />
          ) : (
            <div className="transcribe-result-text">{transcribedText}</div>
          )}

          <div className="transcribe-actions">
            <button className="btn-rerecord" onClick={handleRerecord}>
              重新录制
            </button>
            <button className="btn-confirm" onClick={handleConfirmSend} disabled={isVoiceSubmitting || !transcribedText.trim()}>
              {isVoiceSubmitting ? '发送中...' : '确认发送'}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // 语音模式（默认）
  return (
    <div className="record-page">
      <div className="record-page-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          <BackIcon />
        </button>
        <div className="record-page-title">新记录</div>
      </div>

      {/* 语音录制区域 */}
      <div className="voice-section">
        <div className="record-greeting">
          <div className="record-greeting-time">{getRecordGreeting()}</div>
          <div className="record-greeting-hint">有什么想记录的吗？</div>
        </div>

        <AudioRecorder
          onRecordComplete={handleRecordComplete}
          onError={(error) => console.error('录音错误:', error)}
        />
      </div>

      {/* 分隔线 */}
      <div className="divider-line" />

      {/* 文字输入切换 */}
      <div className="text-input-section">
        <button
          className="text-input-toggle"
          onClick={() => setShowTextInput(true)}
        >
          <EditIcon />
          想打字？点击这里
        </button>
      </div>
    </div>
  )
}
