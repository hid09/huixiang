/**
 * 语音录制组件
 * 支持长按录音、波形动画、时长限制
 * 预请求麦克风权限，提升响应速度
 */
import { useState, useRef, useEffect, useCallback } from 'react'
import { Toast } from 'antd-mobile'
import './AudioRecorder.css'

// 最大录音时长（秒）
const MAX_DURATION = 300 // 5分钟

// 波形动画条数
const WAVE_BARS = 5

interface AudioRecorderProps {
  onRecordComplete?: (audioBlob: Blob, duration: number) => void
  onError?: (error: string) => void
}

export default function AudioRecorder({ onRecordComplete, onError }: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [duration, setDuration] = useState(0)
  const [waveHeights, setWaveHeights] = useState<number[]>(Array(WAVE_BARS).fill(20))
  const [permissionReady, setPermissionReady] = useState(false)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animationRef = useRef<number | null>(null)
  const durationRef = useRef(0)
  const audioContextRef = useRef<AudioContext | null>(null)

  // 清理函数
  const cleanup = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current)
      animationRef.current = null
    }
    // 不在这里停止 stream，保留预请求的权限
  }, [])

  // 完全清理（组件卸载时）
  const fullCleanup = useCallback(() => {
    cleanup()
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
  }, [cleanup])

  // 预请求麦克风权限
  const preRequestPermission = useCallback(async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        return
      }

      console.log('预请求麦克风权限...')
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,  // 语音识别只需 16kHz，减少文件体积
        }
      })

      // 保持 stream 以便快速开始录音
      streamRef.current = stream

      // 设置音频分析器
      const audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(stream)
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      source.connect(analyser)
      analyserRef.current = analyser
      audioContextRef.current = audioContext

      // 静音轨道（预请求时不输出声音）
      stream.getAudioTracks().forEach(track => {
        track.enabled = false
      })

      setPermissionReady(true)
      console.log('麦克风权限预请求成功')
    } catch (error) {
      console.log('预请求权限失败，将在录音时请求:', error)
    }
  }, [])

  // 组件挂载时预请求权限
  useEffect(() => {
    preRequestPermission()
    return () => {
      fullCleanup()
    }
  }, [preRequestPermission, fullCleanup])

  // 更新波形动画
  const updateWaveform = useCallback(() => {
    if (!analyserRef.current) return

    const analyser = analyserRef.current
    const dataArray = new Uint8Array(analyser.frequencyBinCount)
    analyser.getByteFrequencyData(dataArray)

    // 计算波形高度
    const newHeights: number[] = []
    const step = Math.floor(dataArray.length / WAVE_BARS)
    for (let i = 0; i < WAVE_BARS; i++) {
      const value = dataArray[i * step]
      const height = Math.max(20, (value / 255) * 60)
      newHeights.push(height)
    }
    setWaveHeights(newHeights)

    animationRef.current = requestAnimationFrame(updateWaveform)
  }, [])

  // 开始录音
  const startRecording = async () => {
    console.log('开始录音...')

    // 如果正在录音，则停止
    if (isRecording) {
      stopRecording()
      return
    }

    try {
      // 检查是否支持
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        Toast.show({
          content: '当前环境不支持录音，请使用 HTTPS 访问',
          icon: 'fail',
          duration: 3000
        })
        return
      }

      let stream = streamRef.current

      // 如果没有预请求的 stream，现在请求
      if (!stream) {
        console.log('请求麦克风权限...')
        stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 16000,  // 语音识别只需 16kHz，减少文件体积
          }
        })
        console.log('麦克风权限获取成功')
        streamRef.current = stream

        // 设置音频分析器
        const audioContext = new AudioContext()
        const source = audioContext.createMediaStreamSource(stream)
        const analyser = audioContext.createAnalyser()
        analyser.fftSize = 256
        source.connect(analyser)
        analyserRef.current = analyser
        audioContextRef.current = audioContext
      }

      // 启用音频轨道
      stream.getAudioTracks().forEach(track => {
        track.enabled = true
      })

      // 创建 MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4'
      })
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []
      durationRef.current = 0

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mediaRecorder.mimeType })

        // 打印详细日志，方便确认优化是否生效
        const track = streamRef.current?.getAudioTracks()[0]
        const trackSettings = track?.getSettings()
        console.log('🎤 录音完成 ====== ')
        console.log('  时长:', durationRef.current, '秒')
        console.log('  文件大小:', (audioBlob.size / 1024).toFixed(1), 'KB')
        console.log('  采样率:', trackSettings?.sampleRate, 'Hz (预期 16000)')
        console.log('  格式:', mediaRecorder.mimeType)
        console.log('==================')

        // 静音轨道（保持权限但不输出）
        if (streamRef.current) {
          streamRef.current.getAudioTracks().forEach(track => {
            track.enabled = false
          })
        }

        if (onRecordComplete && durationRef.current > 0) {
          onRecordComplete(audioBlob, durationRef.current)
        }
      }

      // 开始录音
      mediaRecorder.start(100)
      setIsRecording(true)
      setDuration(0)

      // 开始计时
      timerRef.current = setInterval(() => {
        durationRef.current += 1
        setDuration(prev => {
          if (prev >= MAX_DURATION) {
            stopRecording()
            Toast.show({ content: '已达到最大录音时长', icon: 'fail' })
            return prev
          }
          return prev + 1
        })
      }, 1000)

      // 开始波形动画
      updateWaveform()

    } catch (error) {
      console.error('录音失败:', error)
      let errorMessage = '无法访问麦克风'
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMessage = '请在浏览器设置中允许麦克风权限'
        } else if (error.name === 'NotFoundError') {
          errorMessage = '未检测到麦克风设备'
        } else if (error.name === 'NotReadableError') {
          errorMessage = '麦克风被其他程序占用'
        } else {
          errorMessage = error.message
        }
      }
      Toast.show({
        content: errorMessage,
        icon: 'fail',
        duration: 3000
      })
      onError?.(errorMessage)
    }
  }

  // 停止录音
  const stopRecording = () => {
    console.log('停止录音')
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    cleanup()
    setIsRecording(false)
    setWaveHeights(Array(WAVE_BARS).fill(20))
  }

  // 格式化时长
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="audio-recorder">
      {/* 录音按钮 */}
      <div className="recorder-main">
        <button
          className={`voice-btn-large ${isRecording ? 'recording' : ''}`}
          onMouseDown={startRecording}
          onMouseUp={stopRecording}
          onMouseLeave={() => isRecording && stopRecording()}
          onTouchStart={(e) => {
            e.preventDefault()
            startRecording()
          }}
          onTouchEnd={(e) => {
            e.preventDefault()
            stopRecording()
          }}
        >
          {isRecording ? (
            <div className="wave-animation">
              {waveHeights.map((height, i) => (
                <div key={i} className="wave-bar" style={{ height: `${height}px` }} />
              ))}
            </div>
          ) : (
            <svg className="mic-icon" viewBox="0 0 24 24">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
            </svg>
          )}
        </button>

        {/* 录音状态提示 */}
        <div className="recorder-status">
          {isRecording ? (
            <>
              <div className="recording-time">{formatDuration(duration)}</div>
              <div className="recording-hint">松开结束录音</div>
            </>
          ) : (
            <div className="recorder-hint">
              {permissionReady ? '长按开始录音' : '点击授权麦克风'}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
