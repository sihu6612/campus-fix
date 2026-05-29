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
  common: { primaryColor: '#4f46e5', primaryColorHover: '#6366f1' },
}

function goBack() {
  if (route.meta.backTo) {
    router.push(route.meta.backTo)
  } else {
    router.back()
  }
}
</script>
