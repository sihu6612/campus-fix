<template>
  <n-config-provider :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <template v-if="!route.meta.layout">
        <router-view v-slot="{ Component }">
          <transition name="page-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </template>
      <AppLayout
        v-else
        :title="route.meta.title || ''"
        :show-back="route.meta.showBack || false"
        :breadcrumbs="route.meta.breadcrumbs || []"
        @back="goBack"
      >
        <router-view v-slot="{ Component: InnerComp }">
          <transition name="page-slide" mode="out-in">
            <component :is="InnerComp" />
          </transition>
        </router-view>
      </AppLayout>
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
