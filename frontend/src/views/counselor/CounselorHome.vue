<template>
  <div class="page-content">
    <n-grid cols="3" x-gap="8" class="stats-grid">
      <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.pending }}</div><div class="stat-label">待分配</div></n-card></n-grid-item>
      <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.in_progress }}</div><div class="stat-label">维修中</div></n-card></n-grid-item>
      <n-grid-item><n-card size="small" class="stat-card"><div class="stat-num">{{ stats.completed }}</div><div class="stat-label">已完成</div></n-card></n-grid-item>
    </n-grid>

    <div class="filter-row">
      <n-select v-if="classOptions.length" v-model:value="selectedClass" :options="classOptions"
        size="small" style="width:160px" @update:value="onClassChange" />
    </div>
    <div class="category-tags">
      <n-tag v-for="cat in allCategories" :key="cat" :type="selectedCategory === cat ? 'primary' : 'default'"
        :checked="selectedCategory === cat" size="small" class="cat-tag" @click="onCategoryClick(cat)">
        {{ cat === '全部' ? '全部' : getCategoryIcon(cat) + ' ' + cat }}
      </n-tag>
    </div>

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
          <StatusBadge :status="o.status" :urgency-score="o.urgency_score || 0" />
          <span class="card-time">{{ fmtTime(o.created_at) }}</span>
        </div>
        <div class="card-title">{{ o.category }} — {{ o.location }}</div>
        <div class="card-desc">{{ o.description.slice(0, 60) }}{{ o.description.length > 60 ? '...' : '' }}</div>
        <div class="card-meta">学生：{{ o.student_name }} · 师傅：{{ o.worker_name || '未分配' }}</div>
      </n-card>
    </div>
    <n-empty v-else description="本班暂无工单" style="margin-top:80px" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '../../composables/useSupabase.js'
import { useAuthStore } from '../../stores/auth.js'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import { CATEGORIES, getCategoryIcon } from '../../composables/useCategories.js'
import StatusBadge from '../../components/StatusBadge.vue'

const router = useRouter()
const auth = useAuthStore()
const store = useOrdersStore()
const tab = ref('all')
const orders = ref([])
const stats = ref({ pending: 0, in_progress: 0, awaiting_confirmation: 0, completed: 0 })
const className = ref('')
const selectedCategory = ref('')
const selectedClass = ref('')
const classOptions = ref([])
const allCategories = computed(() => ['全部', ...CATEGORIES])

async function load(status) {
  await store.fetchOrders(status || null, selectedCategory.value || undefined, selectedClass.value || undefined)
  orders.value = store.orders
}

async function updateStats() {
  const { data: profile } = await supabase.from('profiles').select('class_name').eq('id', auth.userId).single()
  if (!profile?.class_name) return
  className.value = profile.class_name
  if (!classOptions.value.length) {
    classOptions.value = [{ label: profile.class_name, value: profile.class_name }]
    selectedClass.value = profile.class_name
  }

  const { data: students } = await supabase.from('profiles').select('id').eq('class_name', selectedClass.value || profile.class_name).eq('role', 'student')
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

function onCategoryClick(cat) {
  selectedCategory.value = cat === '全部' ? '' : cat
  load(tab.value === 'all' ? null : tab.value)
}
function onClassChange(val) {
  selectedClass.value = val
  load(tab.value === 'all' ? null : tab.value)
  updateStats()
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
.page-content {
  padding: 0 16px 32px;
}
.filter-row {
  margin-top: 4px;
}
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

@media (min-width: 768px) {
  .page-content { padding: 0; }
  .order-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
}
</style>
