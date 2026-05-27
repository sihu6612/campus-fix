<template>
  <n-timeline>
    <n-timeline-item v-for="log in logs" :key="log.id" :type="typeMap[log.to_status] || 'default'">
      <template #header>{{ log.operator_name }}</template>
      <span>{{ log.note }}</span>
      <n-time :time="log.created_at" type="relative" style="display:block;font-size:12px;color:#999;margin-top:4px" />
    </n-timeline-item>
  </n-timeline>
</template>

<script setup>
defineProps({ logs: { type: Array, default: () => [] } })

const typeMap = {
  pending: 'default', assigned: 'info', in_progress: 'info',
  awaiting_confirmation: 'warning', completed: 'success', cancelled: 'error',
}
</script>
