<template>
  <n-tag :type="tagType" :bordered="false" size="small" round>
    {{ label }}
  </n-tag>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ status: String })

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
</script>
