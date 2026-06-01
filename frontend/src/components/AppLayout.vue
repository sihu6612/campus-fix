<template>
  <!-- 移动端布局 -->
  <div v-if="isMobile" class="mobile-layout">
    <header class="mobile-header">
      <div class="header-left">
        <n-button v-if="showBack" text size="small" @click="$emit('back')">
          <n-icon size="20"><ArrowBackOutline /></n-icon>
        </n-button>
        <h2 class="header-title">{{ title }}</h2>
      </div>
      <n-dropdown :options="menuOpts" @select="handleMenu" trigger="click">
        <n-button text><n-icon size="24"><PersonCircleOutline /></n-icon></n-button>
      </n-dropdown>
    </header>

    <main class="mobile-content">
      <slot />
    </main>
  </div>

  <!-- 桌面端布局 -->
  <div v-else class="desktop-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <n-icon size="28" color="#4f46e5"><BuildOutline /></n-icon>
        <span class="brand-text">校修通</span>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isNavActive(item) }"
        >
          <n-icon size="20"><component :is="item.icon" /></n-icon>
          <span>{{ item.label }}</span>
        </router-link>

        <div class="nav-item" @click="toggleAgent">
          <n-icon size="20"><ChatbubblesOutline /></n-icon>
          <span>AI 助手</span>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <n-icon size="20"><PersonCircleOutline /></n-icon>
          <span class="user-name">{{ userName }}</span>
          <span class="user-role">{{ roleLabel }}</span>
        </div>
        <n-button text size="tiny" type="error" @click="handleMenu('logout')">退出</n-button>
      </div>
    </aside>

    <div class="main-area">
      <header class="desktop-header">
        <h2>{{ title }}</h2>
        <n-breadcrumb v-if="breadcrumbs.length">
          <n-breadcrumb-item v-for="b in breadcrumbs" :key="b">{{ b }}</n-breadcrumb-item>
        </n-breadcrumb>
      </header>
      <main class="desktop-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { PersonCircleOutline, ArrowBackOutline, BuildOutline, ListOutline, AddCircleOutline, GridOutline, PeopleOutline, ChatbubblesOutline } from '@vicons/ionicons5'
import { useScreen } from '../composables/useScreen.js'
import { useAuthStore } from '../stores/auth.js'
import { agentPanelOpen } from '../composables/useAgent.js'

const props = defineProps({
  title: { type: String, default: '' },
  showBack: { type: Boolean, default: false },
  breadcrumbs: { type: Array, default: () => [] },
})

defineEmits(['back'])

const { isMobile } = useScreen()
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const userName = computed(() => auth.user?.display_name || auth.user?.email || '用户')
const roleLabel = computed(() => {
  const map = { student: '学生', worker: '师傅', admin: '管理员', counselor: '辅导员' }
  return map[auth.role] || ''
})

import { useDialog, useMessage } from 'naive-ui'

const dialog = useDialog()
const message = useMessage()

const menuOpts = [
  { label: '退出登录', key: 'logout' },
  { label: '删除账号', key: 'deleteAccount' },
]

function handleMenu(key) {
  if (key === 'logout') {
    auth.logout()
    router.push('/login')
  }
  if (key === 'deleteAccount') {
    dialog.warning({
      title: '确认删除账号',
      content: '删除后所有工单和数据将被永久清除，不可恢复。确定要删除吗？',
      positiveText: '确定删除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          const session = JSON.parse(localStorage.getItem('cf_session') || '{}')
          await fetch(`${import.meta.env.VITE_API_BASE || ''}/api/auth/account?user_id=${auth.userId}&access_token=${session.access_token || ''}`, { method: 'DELETE' })
          message.success('账号已删除')
          auth.logout()
          router.push('/login')
        } catch {
          message.error('删除失败，请重试')
        }
      },
    })
  }
}

const navItems = computed(() => {
  switch (auth.role) {
    case 'student':
      return [
        { label: '我的工单', path: '/student', icon: ListOutline },
        { label: '新建报修', path: '/student/create', icon: AddCircleOutline },
      ]
    case 'worker':
      return [
        { label: '工作台', path: '/worker', icon: ListOutline },
      ]
    case 'admin':
      return [
        { label: '仪表盘', path: '/admin', icon: GridOutline },
      ]
    case 'counselor':
      return [
        { label: '班级工单', path: '/counselor', icon: PeopleOutline },
      ]
    default:
      return [{ label: '我的工单', path: '/student', icon: ListOutline }]
  }
})

function isNavActive(item) {
  if (item.path === '/student/create') return route.path === '/student/create'
  return route.path.startsWith(item.path) && !route.path.includes('/create') && !route.path.includes('/order')
}

function toggleAgent() {
  agentPanelOpen.value = !agentPanelOpen.value
}
</script>

<style scoped>
/* ===== 移动端 ===== */
.mobile-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.mobile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 56px;
  padding: 0 16px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
  background: #fff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.mobile-content {
  flex: 1;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* ===== 桌面端 ===== */
.desktop-layout {
  height: 100vh;
  display: flex;
  background: #f0f2f5;
}

.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 20px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.brand-text {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  letter-spacing: 1px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  color: #555;
  text-decoration: none;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.15s;
}

.nav-item:hover {
  background: #f5f3ff;
  color: #4f46e5;
}

.nav-item.active {
  background: #ede9fe;
  color: #4f46e5;
  font-weight: 600;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.user-name {
  color: #333;
  font-weight: 500;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role {
  color: #4f46e5;
  font-size: 11px;
  background: #ede9fe;
  padding: 1px 8px;
  border-radius: 10px;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.desktop-header {
  height: 56px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
}

.desktop-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.desktop-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
