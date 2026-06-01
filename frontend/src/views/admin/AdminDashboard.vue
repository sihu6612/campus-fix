<template>
  <div class="page-content">
    <n-grid cols="3" x-gap="8" class="stats-grid">
      <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.pending }}</div><div class="stat-label">待分配</div></n-card></n-grid-item>
      <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.in_progress }}</div><div class="stat-label">维修中</div></n-card></n-grid-item>
      <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.completed }}</div><div class="stat-label">已完成</div></n-card></n-grid-item>
    </n-grid>

    <!-- 类别标签 -->
    <div v-if="tab !== 'users' && tab !== 'categories'" class="category-tags">
      <n-tag v-for="cat in allCategories" :key="cat" :type="selectedCategory === cat ? 'primary' : 'default'"
        :checked="selectedCategory === cat" size="small" class="cat-tag" @click="onCategoryClick(cat)">
        {{ cat === '全部' ? '全部' : getCategoryIcon(cat) + ' ' + cat }}
      </n-tag>
    </div>

    <!-- 批量操作栏 -->
    <div v-if="checkedIds.length && tab !== 'users' && tab !== 'categories'" class="batch-bar">
      <span class="batch-info">已选 {{ checkedIds.length }} 项</span>
      <n-select v-model:value="batchWorkerId" :options="workerOpts" placeholder="选择师傅" size="small" style="width:150px" />
      <n-button size="small" type="primary" @click="batchAssign">批量分配</n-button>
      <n-button size="small" type="warning" @click="batchClose">批量关闭</n-button>
      <n-button size="small" @click="checkedIds = []">取消</n-button>
    </div>

    <n-tabs v-model:value="tab" type="line" @update:value="onTabChange">
      <n-tab-pane name="all" tab="全部" />
      <n-tab-pane name="pending" tab="待分配" />
      <n-tab-pane name="in_progress" tab="维修中" />
      <n-tab-pane name="completed" tab="已完成" />
      <n-tab-pane name="categories" tab="类别管理" />
      <n-tab-pane name="users" tab="用户管理" />
    </n-tabs>

    <!-- 桌面端使用表格 -->
    <n-data-table
      v-if="orders.length && tab !== 'users' && tab !== 'categories'"
      :columns="tableColumns"
      :data="orders"
      :row-key="r => r.id"
      :checked-row-keys="checkedIds"
      :row-props="row => ({ style: 'cursor:pointer', onClick: () => goOrder(row.id) })"
      @update:checked-row-keys="v => checkedIds = v"
      class="order-table"
    />

    <!-- 移动端使用卡片 -->
    <div v-if="orders.length && tab !== 'users' && tab !== 'categories'" class="order-list">
      <n-card v-for="o in orders" :key="o.id" size="small" class="order-card" hoverable @click="goOrder(o.id)">
        <div class="card-row">
          <StatusBadge :status="o.status" />
          <span class="card-time">{{ fmtTime(o.created_at) }}</span>
        </div>
        <div class="card-title">{{ o.category }} — {{ o.location }}</div>
        <div class="card-desc">{{ o.description.slice(0, 60) }}{{ o.description.length > 60 ? '...' : '' }}</div>
        <div class="card-meta">学生：{{ o.student_name }} · 师傅：{{ o.worker_name || '未分配' }}</div>
        <div style="margin-top:8px;display:flex;gap:6px">
          <n-button v-if="o.status === 'pending'" size="small" type="primary" @click.stop="showAssign(o)">分配</n-button>
          <n-button size="small" @click.stop="showEdit(o)">编辑</n-button>
          <n-button size="small" type="error" @click.stop="confirmDelete(o)">删除</n-button>
        </div>
      </n-card>
    </div>
    <n-empty v-else-if="tab !== 'users' && tab !== 'categories'" description="暂无工单" style="margin-top:80px" />

    <!-- 类别管理 -->
    <div v-if="tab === 'categories'" class="category-panel" style="margin-top:12px">
      <div class="category-list">
        <n-tag v-for="cat in manageCategories" :key="cat" closable :type="CATEGORIES.includes(cat) ? 'info' : 'default'"
          @close="removeCategory(cat)" :disabled="CATEGORIES.includes(cat)">
          {{ cat }}
        </n-tag>
      </div>
      <div style="display:flex;gap:8px;margin-top:12px">
        <n-input v-model:value="newCategoryName" placeholder="新类别名称" style="flex:1" size="small" />
        <n-button type="primary" size="small" @click="addCategory">添加</n-button>
      </div>
    </div>

    <!-- 用户管理 -->
    <div v-if="tab === 'users'" class="user-panel" style="margin-top:12px">
      <n-data-table
        v-if="users.length"
        :columns="userColumns"
        :data="users"
        :row-key="r => r.id"
        :row-props="() => ({ style: 'cursor:default' })"
      />
      <n-empty v-else description="加载中..." style="margin-top:40px" />
    </div>

    <n-modal v-model:show="assignModal" preset="card" title="分配师傅">
      <n-form-item label="师傅">
        <n-select v-model:value="assignWorkerId" placeholder="选择师傅" :options="workerOpts" />
      </n-form-item>
      <n-button type="primary" block :loading="assigning" @click="doAssign">确认分配</n-button>
    </n-modal>

    <n-modal v-model:show="editModal" preset="card" title="编辑工单" style="max-width:480px">
      <n-form-item label="类别">
        <n-select v-model:value="editForm.category" :options="allCategories.filter(c => c !== '全部').map(c => ({ label: c, value: c }))" />
      </n-form-item>
      <n-form-item label="位置">
        <n-input v-model:value="editForm.location" />
      </n-form-item>
      <n-form-item label="描述">
        <n-input v-model:value="editForm.description" type="textarea" :autosize="{ minRows: 2, maxRows: 4 }" />
      </n-form-item>
      <n-form-item label="紧急程度">
        <n-select v-model:value="editForm.urgency" :options="urgencyOptions" />
      </n-form-item>
      <n-form-item label="状态">
        <n-select v-model:value="editForm.status" :options="statusOptions" />
      </n-form-item>
      <n-button type="primary" block :loading="saving" @click="saveEdit">保存修改</n-button>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog, NTag, NButton, NCheckbox } from 'naive-ui'
import { supabase } from '../../composables/useSupabase.js'
import { useOrdersStore } from '../../stores/orders.js'
import { useAuthStore } from '../../stores/auth.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import { CATEGORIES, getCategoryIcon } from '../../composables/useCategories.js'
import StatusBadge from '../../components/StatusBadge.vue'
import { useScreen } from '../../composables/useScreen.js'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const store = useOrdersStore()
const auth = useAuthStore()
const { isMobile } = useScreen()
const tab = ref('all')
const orders = ref([])
const workers = ref([])
const assignModal = ref(false)
const assignOrderId = ref(null)
const assignWorkerId = ref(null)
const assigning = ref(false)
const stats = ref({ pending: 0, in_progress: 0, completed: 0 })
const users = ref([])
const selectedCategory = ref('')
const allCategories = computed(() => ['全部', ...CATEGORIES])

// 批量操作
const checkedIds = ref([])
const batchWorkerId = ref(null)

// 编辑工单
const editModal = ref(false)
const editForm = ref({ id: '', category: '', location: '', description: '', urgency: 'normal', status: '' })
const saving = ref(false)

// 类别管理
const manageCategories = ref([...CATEGORIES])
const newCategoryName = ref('')

const roleLabel = { student: '学生', worker: '维修师傅', admin: '管理员', counselor: '辅导员' }

const workerOpts = ref([])

const statusMap = {
  pending: '待分配', assigned: '已分配', in_progress: '维修中',
  awaiting_confirmation: '待确认', completed: '已完成', cancelled: '已取消',
}
const typeMap = { pending: 'warning', assigned: 'info', in_progress: 'info', awaiting_confirmation: 'success', completed: 'default', cancelled: 'default' }

const statusOptions = [
  { label: '待分配', value: 'pending' }, { label: '已分配', value: 'assigned' },
  { label: '维修中', value: 'in_progress' }, { label: '待确认', value: 'awaiting_confirmation' },
  { label: '已完成', value: 'completed' }, { label: '已取消', value: 'cancelled' },
]
const urgencyOptions = [{ label: '普通', value: 'normal' }, { label: '紧急', value: 'urgent' }]

const tableColumns = computed(() => [
  { type: 'selection', width: 40 },
  { title: '状态', key: 'status', width: 90, render: (row) => h(NTag, { type: typeMap[row.status] || 'default', size: 'small' }, () => statusMap[row.status] || row.status) },
  { title: '类型', key: 'category', width: 90 },
  { title: '位置', key: 'location', width: 120, ellipsis: { tooltip: true } },
  { title: '描述', key: 'description', ellipsis: { tooltip: true }, render: (row) => row.description?.slice(0, 30) + (row.description?.length > 30 ? '...' : '') },
  { title: '学生', key: 'student_name', width: 80 },
  { title: '师傅', key: 'worker_name', width: 80, render: (row) => row.worker_name || '-' },
  { title: '时间', key: 'created_at', width: 100, render: (row) => fmtTime(row.created_at) },
  { title: '操作', key: 'actions', width: 120, render: (row) => {
    const btns = []
    if (row.status === 'pending') btns.push(h(NButton, { size: 'tiny', type: 'primary', onClick: (e) => { e.stopPropagation(); showAssign(row) } }, () => '分配'))
    btns.push(h(NButton, { size: 'tiny', style: 'margin-left:4px', onClick: (e) => { e.stopPropagation(); showEdit(row) } }, () => '编辑'))
    btns.push(h(NButton, { size: 'tiny', type: 'error', style: 'margin-left:4px', onClick: (e) => { e.stopPropagation(); confirmDelete(row) } }, () => '删除'))
    return btns
  }},
])

const userColumns = computed(() => [
  { title: '名称', key: 'display_name', width: 120 },
  { title: '角色', key: 'role', width: 100, render: (row) => roleLabel[row.role] || row.role },
  { title: '班级', key: 'class_name', width: 140, render: (row) => row.class_name || '-' },
  { title: '手机', key: 'phone', width: 120, render: (row) => row.phone || '-' },
  { title: '注册时间', key: 'created_at', width: 110, render: (row) => fmtTime(row.created_at) },
  { title: '操作', key: 'actions', width: 80, render: (row) => h(NButton, { size: 'tiny', type: 'error', onClick: () => deleteUser(row) }, () => '删除') },
])

async function refreshStats() {
  const all = await supabase.from('repair_orders').select('status')
  if (all.data) {
    stats.value = {
      pending: all.data.filter(o => o.status === 'pending').length,
      in_progress: all.data.filter(o => o.status === 'in_progress').length,
      completed: all.data.filter(o => o.status === 'completed').length,
    }
  }
}

async function load(status) {
  await store.fetchOrders(status || null, selectedCategory.value || undefined)
  orders.value = store.orders
  refreshStats()
}

async function loadWorkers() {
  const res = await supabase.from('profiles').select('id,display_name').eq('role', 'worker')
  if (res.data) {
    workers.value = res.data
    workerOpts.value = res.data.map(w => ({ label: w.display_name, value: w.id }))
  }
}

function onCategoryClick(cat) {
  selectedCategory.value = cat === '全部' ? '' : cat
  load(tab.value === 'all' ? null : tab.value)
}

function onTabChange(val) {
  checkedIds.value = []
  if (val === 'users') { loadUsers(); return }
  if (val === 'categories') { loadCategories(); return }
  load(val === 'all' ? null : val)
}
function goOrder(id) { router.push(`/admin/order/${id}`) }
function fmtTime(t) { return t ? new Date(t).toLocaleDateString('zh-CN') : '' }

async function loadUsers() {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE || ''}/api/auth/admin/users?admin_id=${auth.userId}`)
    if (!res.ok) throw new Error('加载失败')
    users.value = await res.json()
  } catch (e) { message.error(e.message) }
}

async function deleteUser(row) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除用户「${row.display_name}」吗？此操作不可撤销。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_BASE || ''}/api/auth/admin/users/${row.id}?admin_id=${auth.userId}`, { method: 'DELETE' })
        if (!res.ok) throw new Error('删除失败')
        message.success('已删除')
        loadUsers()
      } catch (e) { message.error(e.message) }
    },
  })
}

// --- 编辑工单 ---
function showEdit(order) {
  editForm.value = {
    id: order.id,
    category: order.category,
    location: order.location,
    description: order.description,
    urgency: order.urgency || 'normal',
    status: order.status,
  }
  editModal.value = true
}

async function saveEdit() {
  saving.value = true
  try {
    const { id, ...updates } = editForm.value
    await store.updateOrder(id, updates)
    message.success('修改已保存')
    editModal.value = false
    load(tab.value === 'all' ? null : tab.value)
    refreshStats()
  } catch (e) { message.error(e.message) }
  saving.value = false
}

// --- 删除工单 ---
function confirmDelete(order) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除工单「${order.category} - ${order.location}」吗？此操作不可撤销。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await store.hardDeleteOrder(order.id)
        message.success('工单已删除')
        load(tab.value === 'all' ? null : tab.value)
        refreshStats()
      } catch (e) { message.error(e.message) }
    },
  })
}

// --- 批量操作 ---
async function batchAssign() {
  if (!batchWorkerId.value) { message.warning('请选择师傅'); return }
  if (!checkedIds.value.length) { message.warning('请选择工单'); return }
  try {
    await store.batchUpdateOrders(checkedIds.value, { worker_id: batchWorkerId.value, status: 'assigned' })
    message.success(`已分配 ${checkedIds.value.length} 个工单`)
    checkedIds.value = []
    load(tab.value === 'all' ? null : tab.value)
    refreshStats()
  } catch (e) { message.error(e.message) }
}

async function batchClose() {
  if (!checkedIds.value.length) { message.warning('请选择工单'); return }
  dialog.warning({
    title: '批量关闭',
    content: `确定关闭 ${checkedIds.value.length} 个工单吗？`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await store.batchUpdateOrders(checkedIds.value, { status: 'completed' })
        message.success(`已关闭 ${checkedIds.value.length} 个工单`)
        checkedIds.value = []
        load(tab.value === 'all' ? null : tab.value)
        refreshStats()
      } catch (e) { message.error(e.message) }
    },
  })
}

// --- 类别管理 ---
async function loadCategories() {
  try { manageCategories.value = await store.fetchCategories() }
  catch { manageCategories.value = [...CATEGORIES] }
}

async function addCategory() {
  if (!newCategoryName.value.trim()) return
  try {
    await fetch(`${import.meta.env.VITE_API_BASE || ''}/api/orders/categories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newCategoryName.value.trim() }),
    })
    message.success('已添加')
    newCategoryName.value = ''
    loadCategories()
  } catch (e) { message.error(e.message) }
}

async function removeCategory(name) {
  if (CATEGORIES.includes(name)) { message.warning('内置类别不可删除'); return }
  try {
    await fetch(`${import.meta.env.VITE_API_BASE || ''}/api/orders/categories/${encodeURIComponent(name)}`, { method: 'DELETE' })
    message.success('已删除')
    loadCategories()
  } catch (e) { message.error(e.message) }
}

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
    refreshStats()
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

.category-tags {
  display: flex;
  gap: 8px;
  margin: 8px 0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  flex-wrap: wrap;
}
.category-tags::-webkit-scrollbar { display: none; }
.cat-tag { cursor: pointer; flex-shrink: 0; }

.batch-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f3ff;
  border-radius: 10px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.batch-info { font-size: 13px; color: #4f46e5; font-weight: 600; white-space: nowrap; }

.category-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

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
