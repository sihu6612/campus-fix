<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <router-view v-slot="{ Component, route: r }">
        <transition name="page-slide" mode="out-in">
          <component :is="Component" :key="r.path" v-if="!r.meta.layout" />
          <AppLayout
            v-else
            :key="r.path + '-layout'"
            :title="r.meta.title || ''"
            :show-back="r.meta.showBack || false"
            :breadcrumbs="r.meta.breadcrumbs || []"
            @back="goBack"
          >
            <component :is="Component" :key="r.path" />
          </AppLayout>
        </transition>
      </router-view>
      <AgentChat v-if="showAgent" />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { zhCN, dateZhCN } from 'naive-ui'
import AppLayout from './components/AppLayout.vue'
import AgentChat from './components/AgentChat.vue'

const route = useRoute()
const router = useRouter()

const showAgent = computed(() => route.path !== '/login')

const themeOverrides = {
  common: {
    primaryColor: '#4f46e5',
    primaryColorHover: '#6366f1',
    primaryColorPressed: '#4338ca',
    primaryColorSuppl: '#6366f1',
    borderRadius: '8px',
    borderRadiusSmall: '6px',
    fontSize: '15px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
  },
  Button: {
    borderRadiusSmall: '6px',
    borderRadiusMedium: '8px',
    borderRadiusLarge: '12px',
    textColor: '#4f46e5',
    border: '1px solid #e2e8f0',
    textColorGhost: '#64748b',
    borderHover: '1px solid #4f46e5',
    colorHover: '#ede9fe',
    textColorHover: '#4f46e5',
  },
  Input: {
    borderRadius: '8px',
    border: '1px solid #e2e8f0',
    borderHover: '1px solid #6366f1',
    borderFocus: '1px solid #4f46e5',
    boxShadowFocus: '0 0 0 3px rgba(79,70,229,0.12)',
  },
  Card: {
    borderRadius: '12px',
    paddingSmall: '12px',
    paddingMedium: '16px',
    paddingLarge: '20px',
    titleFontSizeSmall: '15px',
    titleFontSizeMedium: '16px',
    borderColor: '#f1f5f9',
  },
  Tag: {
    borderRadius: '6px',
  },
  Tabs: {
    tabTextColor: '#64748b',
    barColor: '#4f46e5',
  },
  Dialog: {
    borderRadius: '16px',
  },
  Select: {
    peers: {
      InternalSelection: {
        borderRadius: '8px',
        border: '1px solid #e2e8f0',
      },
    },
  },
}

function goBack() {
  if (route.meta.backTo) {
    router.push(route.meta.backTo)
  } else {
    router.back()
  }
}
</script>
