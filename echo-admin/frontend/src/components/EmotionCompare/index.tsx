// 情绪对比组件 - ASR情绪 vs 文本情绪
import React from 'react';
import { Tag, Tooltip } from 'antd';
import type { EmotionCompareProps } from './types';

const EmotionCompare: React.FC<EmotionCompareProps> = ({
  emotionType,
  asrEmotion,
  moodTag,
}) => {
  // 情绪类型映射
  const getEmotionConfig = (type: string) => {
    const configs: Record<string, { color: string; text: string }> = {
      positive: { color: 'success', text: '积极' },
      neutral: { color: 'default', text: '平静' },
      negative: { color: 'error', text: '消极' },
      mixed: { color: 'warning', text: '复杂' },
      happy: { color: 'success', text: '开心' },
      sad: { color: 'error', text: '难过' },
      angry: { color: 'error', text: '愤怒' },
      neutral_voice: { color: 'default', text: '平静' },
      fear: { color: 'warning', text: '恐惧' },
      disgust: { color: 'warning', text: '厌恶' },
      surprise: { color: 'processing', text: '惊讶' },
    };
    return configs[type] || { color: 'default', text: type || '-' };
  };

  const textConfig = getEmotionConfig(emotionType);
  const asrConfig = getEmotionConfig(asrEmotion || '');

  // 检查情绪是否一致（简化判断逻辑）
  const isMismatch = asrEmotion && emotionType !== asrEmotion;

  return (
    <div className="emotion-compare">
      <Tag color={textConfig.color}>
        文本: {textConfig.text}
      </Tag>
      {asrEmotion && (
        <Tag color={asrConfig.color} className={isMismatch ? 'mismatch' : ''}>
          语音: {asrConfig.text}
        </Tag>
      )}
      {moodTag && (
        <Tooltip title="情绪标签">
          <Tag color="purple">{moodTag}</Tag>
        </Tooltip>
      )}
      {isMismatch && (
        <Tooltip title="语音情绪与文本情绪不一致">
          <span style={{ color: '#ff6b6b', fontSize: 12 }}>⚠️</span>
        </Tooltip>
      )}
    </div>
  );
};

export default EmotionCompare;
