<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <router-view />
      <AgentChat v-if="showAgent" />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { zhCN, dateZhCN } from 'naive-ui'
import AgentChat from './components/AgentChat.vue'

const route = useRoute()
const showAgent = computed(() => route.path !== '/login')

const themeOverrides = {
  common: { primaryColor: '#4f46e5', primaryColorHover: '#6366f1' },
}
</script>
