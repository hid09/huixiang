/**
 * 空状态组件
 */
import './Empty.css'

interface EmptyProps {
  icon?: string
  title?: string
  description?: string
}

export default function Empty({
  icon = '📝',
  title = '暂无内容',
  description = ''
}: EmptyProps) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <h3 className="empty-title">{title}</h3>
      {description && <p className="empty-description">{description}</p>}
    </div>
  )
}
