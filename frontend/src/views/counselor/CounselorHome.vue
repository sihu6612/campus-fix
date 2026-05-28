<template>
  <div class="app-shell">
    <n-layout>
      <n-layout-header bordered class="app-header">
        <div class="header-inner">
          <h2>班级管理 · {{ className }}</h2>
          <n-dropdown :options="menuOpts" @select="handleMenu">
            <n-button text><n-icon size="24"><PersonCircleOutline /></n-icon></n-button>
          </n-dropdown>
        </div>
      </n-layout-header>

      <n-layout-content class="app-content">
        <n-grid cols="3" x-gap="8" style="margin-bottom:16px">
          <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.pending }}</div><div class="stat-label">待分配</div></n-card></n-grid-item>
          <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.in_progress }}</div><div class="stat-label">维修中</div></n-card></n-grid-item>
          <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.completed }}</div><div class="stat-label">已完成</div></n-card></n-grid-item>
        </n-grid>

        <n-tabs v-model:value="tab" type="line" @update:value="onTabChange">
          <n-tab-pane name="all" tab="全部" />
          <n-tab-pane name="pending" tab="待分配" />
          <n-tab-pane name="in_progress" tab="维修中" />
          <n-tab-pane name="awaiting_confirmation" tab="待确认" />
          <n-tab-pane name="completed" tab="已完成" />
        </n-tabs>

        <div v-if="orders.length" class="order-list">
          <n-card v-for="o in orders" :key="o.id" size="small" class="order-card" hoverable @click="goOrder(o.id)">
            <div class="card-row">
              <StatusBadge :status="o.status" />
              <span class="card-time">{{ fmtTime(o.created_at) }}</span>
            </div>
            <div class="card-title">{{ o.category }} — {{ o.location }}</div>
            <div class="card-desc">{{ o.description.slice(0, 60) }}{{ o.description.length > 60 ? '...' : '' }}</div>
            <div class="card-meta">学生：{{ o.student_name }} · 师傅：{{ o.worker_name || '未分配' }}</div>
          </n-card>
        </div>
        <n-empty v-else description="本班暂无工单" style="margin-top:80px" />
      </n-layout-content>
    </n-layout>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PersonCircleOutline } from '@vicons/ionicons5'
import { supabase } from '../../composables/useSupabase.js'
import { useAuthStore } from '../../stores/auth.js'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import StatusBadge from '../../components/StatusBadge.vue'

const router = useRouter()
const auth = useAuthStore()
const store = useOrdersStore()
const tab = ref('all')
const orders = ref([])
const stats = ref({ pending: 0, in_progress: 0, awaiting_confirmation: 0, completed: 0 })
const className = ref('')

const menuOpts = [{ label: '退出登录', key: 'logout' }]

function handleMenu(key) {
  if (key === 'logout') { auth.logout(); router.push('/login') }
}

async function load(status) {
  await store.fetchOrders(status || null)
  orders.value = store.orders
  updateStats()
}

async function updateStats() {
  // 获取本班全部工单统计
  const { data: profile } = await supabase.from('profiles').select('class_name').eq('id', auth.userId).single()
  if (!profile?.class_name) return
  className.value = profile.class_name

  const { data: students } = await supabase.from('profiles').select('id').eq('class_name', profile.class_name).eq('role', 'student')
  if (!students?.length) return
  const ids = students.map(s => s.id)

  const { data: all } = await supabase.from('repair_orders').select('status').in('student_id', ids)
  if (all) {
    stats.value = {
      pending: all.filter(o => o.status === 'pending').length,
      in_progress: all.filter(o => o.status === 'in_progress').length,
      awaiting_confirmation: all.filter(o => o.status === 'awaiting_confirmation').length,
      completed: all.filter(o => o.status === 'completed').length,
    }
  }
}

function onTabChange(val) { load(val === 'all' ? null : val) }
function goOrder(id) { router.push(`/counselor/order/${id}`) }
function fmtTime(t) { return t ? new Date(t).toLocaleDateString('zh-CN') : '' }

onMounted(() => {
  load()
  subscribeOrders(() => load(tab.value === 'all' ? null : tab.value))
})
</script>

<style scoped>
.app-shell { height: 100vh; display: flex; flex-direction: column; }
.app-header { padding: 0 16px; }
.header-inner { display: flex; justify-content: space-between; align-items: center; height: 56px; }
.header-inner h2 { font-size: 18px; }
.app-content { flex: 1; overflow-y: auto; padding: 0 16px 80px; }
.stat-card { text-align: center; border-radius: 12px; }
.stat-num { font-size: 28px; font-weight: 700; color: #4f46e5; }
.stat-label { font-size: 12px; color: #999; margin-top: 4px; }
.order-list { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
.order-card { border-radius: 12px; }
.card-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.card-time { font-size: 12px; color: #aaa; }
.card-title { font-size: 15px; font-weight: 600; color: #333; }
.card-desc { font-size: 13px; color: #888; margin-top: 4px; }
.card-meta { font-size: 12px; color: #aaa; margin-top: 4px; }

@media (min-width: 768px) {
  .app-shell { background: #f0f2f5; }
  .app-header { padding: 0; }
  .header-inner { max-width: 960px; margin: 0 auto; padding: 0 16px; }
  .app-content { max-width: 960px; margin: 0 auto; padding: 16px 0 40px; }
  .order-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
}
</style>
