<template>
  <div class="app-shell">
    <n-layout>
      <n-layout-header bordered class="app-header">
        <div class="header-inner">
          <h2>物业管理</h2>
          <n-dropdown :options="menuOpts" @select="handleMenu">
            <n-button text><n-icon size="24"><PersonCircleOutline /></n-icon></n-button>
          </n-dropdown>
        </div>
      </n-layout-header>

      <n-layout-content class="app-content">
        <!-- 统计栏 -->
        <n-grid cols="3" x-gap="8" style="margin-bottom:16px">
          <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.pending }}</div><div class="stat-label">待分配</div></n-card></n-grid-item>
          <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.in_progress }}</div><div class="stat-label">维修中</div></n-card></n-grid-item>
          <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.completed }}</div><div class="stat-label">已完成</div></n-card></n-grid-item>
        </n-grid>

        <n-tabs v-model:value="tab" type="line" @update:value="onTabChange">
          <n-tab-pane name="all" tab="全部" />
          <n-tab-pane name="pending" tab="待分配" />
          <n-tab-pane name="in_progress" tab="维修中" />
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
            <div v-if="o.status === 'pending'" style="margin-top:8px">
              <n-button size="small" type="primary" @click.stop="showAssign(o)">分配师傅</n-button>
            </div>
          </n-card>
        </div>
        <n-empty v-else description="暂无工单" style="margin-top:80px" />
      </n-layout-content>
    </n-layout>

    <!-- 分配弹窗 -->
    <n-modal v-model:show="assignModal" preset="card" title="分配师傅">
      <n-form-item label="师傅">
        <n-select v-model:value="assignWorkerId" placeholder="选择师傅" :options="workerOpts" />
      </n-form-item>
      <n-button type="primary" block :loading="assigning" @click="doAssign">确认分配</n-button>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { PersonCircleOutline } from '@vicons/ionicons5'
import { supabase } from '../../composables/useSupabase.js'
import { useAuthStore } from '../../stores/auth.js'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import StatusBadge from '../../components/StatusBadge.vue'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()
const store = useOrdersStore()
const tab = ref('all')
const orders = ref([])
const workers = ref([])
const assignModal = ref(false)
const assignOrderId = ref(null)
const assignWorkerId = ref(null)
const assigning = ref(false)
const stats = ref({ pending: 0, in_progress: 0, completed: 0 })

const menuOpts = [{ label: '退出登录', key: 'logout' }]

const workerOpts = ref([])

function handleMenu(key) {
  if (key === 'logout') { auth.logout(); router.push('/login') }
}

async function load(status) {
  await store.fetchOrders(status || null)
  orders.value = store.orders
  // 统计
  const all = await supabase.from('repair_orders').select('status')
  if (all.data) {
    stats.value = {
      pending: all.data.filter(o => o.status === 'pending').length,
      in_progress: all.data.filter(o => o.status === 'in_progress').length,
      completed: all.data.filter(o => o.status === 'completed').length,
    }
  }
}

async function loadWorkers() {
  const res = await supabase.from('profiles').select('id,display_name').eq('role', 'worker')
  if (res.data) {
    workers.value = res.data
    workerOpts.value = res.data.map(w => ({ label: w.display_name, value: w.id }))
  }
}

function onTabChange(val) { load(val === 'all' ? null : val) }
function goOrder(id) { router.push(`/admin/order/${id}`) }
function fmtTime(t) { return t ? new Date(t).toLocaleDateString('zh-CN') : '' }

function showAssign(order) {
  assignOrderId.value = order.id
  assignWorkerId.value = null
  assignModal.value = true
}

async function doAssign() {
  if (!assignWorkerId.value) { message.warning('请选择师傅'); return }
  assigning.value = true
  try {
    await store.updateOrder(assignOrderId.value, { worker_id: assignWorkerId.value, status: 'assigned' })
    message.success('分配成功')
    assignModal.value = false
    load(tab.value === 'all' ? null : tab.value)
  } catch (e) { message.error(e.message) }
  assigning.value = false
}

onMounted(async () => {
  await loadWorkers()
  load()
  subscribeOrders(() => load(tab.value === 'all' ? null : tab.value))
})
</script>

<style scoped>
.app-shell { height: 100vh; display: flex; flex-direction: column; }
.app-header { padding: 0 16px; }
.header-inner { display: flex; justify-content: space-between; align-items: center; height: 56px; }
.header-inner h2 { font-size: 18px; }
.app-content { flex: 1; overflow-y: auto; padding: 16px 16px 80px; }
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
</style>
