export const CATEGORIES = [
  '电路/灯具',
  '供水/管道',
  '家具/门窗',
  '空调/电器',
  '网络/弱电',
  '墙面/渗水',
  '锁具/五金',
  '卫生/下水',
  '其它',
]

export const CATEGORY_ICONS = {
  '电路/灯具': '💡',
  '供水/管道': '🚿',
  '家具/门窗': '🪟',
  '空调/电器': '❄️',
  '网络/弱电': '📶',
  '墙面/渗水': '🧱',
  '锁具/五金': '🔑',
  '卫生/下水': '🚽',
}

export function getCategoryIcon(cat) {
  return CATEGORY_ICONS[cat] || '🔧'
}
