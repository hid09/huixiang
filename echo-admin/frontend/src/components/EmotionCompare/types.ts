// 情绪对比组件类型定义
export interface EmotionCompareProps {
  /** 文本情绪类型 */
  emotionType: string;
  /** ASR 语音情绪（可选） */
  asrEmotion?: string;
  /** 情绪标签 */
  moodTag?: string;
}
