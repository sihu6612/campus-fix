<template>
  <n-tag :type="tagType" :bordered="false" size="small" round>
    {{ label }}
  </n-tag>
  <n-tag v-if="urgencyScore > 0" :type="urgencyType" :bordered="false" size="small" round style="margin-left:4px">
    {{ urgencyLabel }}
  </n-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: String,
  urgencyScore: { type: Number, default: 0 },
})

const map = {
  pending: { type: 'warning', label: '待分配' },
  assigned: { type: 'info', label: '已分配' },
  in_progress: { type: 'info', label: '维修中' },
  awaiting_confirmation: { type: 'warning', label: '待确认' },
  completed: { type: 'success', label: '已完成' },
  cancelled: { type: 'default', label: '已取消' },
}

const tagType = computed(() => map[props.status]?.type || 'default')
const label = computed(() => map[props.status]?.label || props.status)

const urgencyType = computed(() => {
  const s = props.urgencyScore || 0
  if (s >= 80) return 'error'
  if (s >= 40) return 'warning'
  return 'default'
})
const urgencyLabel = computed(() => {
  const s = props.urgencyScore || 0
  if (s >= 90) return `紧急 ${s}`
  if (s >= 80) return `较急 ${s}`
  if (s >= 40) return `中等 ${s}`
  return `普通 ${s}`
})
</script>
