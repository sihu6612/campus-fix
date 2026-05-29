<template>
  <div class="page-content">
    <n-grid cols="3" x-gap="8" class="stats-grid">
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

    <!-- 桌面端使用表格 -->
    <n-data-table
      v-if="orders.length"
      :columns="tableColumns"
      :data="orders"
      :row-key="r => r.id"
      :row-props="row => ({ style: 'cursor:pointer', onClick: () => goOrder(row.id) })"
      class="order-table"
    />

    <!-- 移动端使用卡片 -->
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

    <n-modal v-model:show="assignModal" preset="card" title="分配师傅">
      <n-form-item label="师傅">
        <n-select v-model:value="assignWorkerId" placeholder="选择师傅" :options="workerOpts" />
      </n-form-item>
      <n-button type="primary" block :loading="assigning" @click="doAssign">确认分配</n-button>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NTag, NButton } from 'naive-ui'
import { supabase } from '../../composables/useSupabase.js'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import StatusBadge from '../../components/StatusBadge.vue'
import { useScreen } from '../../composables/useScreen.js'

const router = useRouter()
const message = useMessage()
const store = useOrdersStore()
const { isMobile } = useScreen()
const tab = ref('all')
const orders = ref([])
const workers = ref([])
const assignModal = ref(false)
const assignOrderId = ref(null)
const assignWorkerId = ref(null)
const assigning = ref(false)
const stats = ref({ pending: 0, in_progress: 0, completed: 0 })

const workerOpts = ref([])

const statusMap = {
  pending: '待分配', assigned: '已分配', in_progress: '维修中',
  awaiting_confirmation: '待确认', completed: '已完成',
}
const typeMap = { pending: 'warning', assigned: 'info', in_progress: 'info', awaiting_confirmation: 'success', completed: 'default' }

const tableColumns = computed(() => [
  { title: '状态', key: 'status', width: 100, render: (row) => h(NTag, { type: typeMap[row.status] || 'default', size: 'small' }, () => statusMap[row.status] || row.status) },
  { title: '类型', key: 'category', width: 100 },
  { title: '位置', key: 'location', width: 140, ellipsis: { tooltip: true } },
  { title: '描述', key: 'description', ellipsis: { tooltip: true }, render: (row) => row.description?.slice(0, 40) + (row.description?.length > 40 ? '...' : '') },
  { title: '学生', key: 'student_name', width: 100 },
  { title: '师傅', key: 'worker_name', width: 100, render: (row) => row.worker_name || '-' },
  { title: '时间', key: 'created_at', width: 110, render: (row) => fmtTime(row.created_at) },
  { title: '操作', key: 'actions', width: 100, render: (row) => row.status === 'pending' ? h(NButton, { size: 'tiny', type: 'primary', onClick: (e) => { e.stopPropagation(); showAssign(row) } }, () => '分配') : null },
])

async function load(status) {
  await store.fetchOrders(status || null)
  orders.value = store.orders
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
.page-content {
  padding: 0 16px 32px;
}
.stats-grid { margin-bottom: 16px; }
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

.order-table { display: none; }

@media (min-width: 768px) {
  .page-content { padding: 0; }
  .order-list { display: none; }
  .order-table { display: block; }
}
</style>
