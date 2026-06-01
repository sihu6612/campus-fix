<template>
  <div class="page-content">
    <div class="route-btn-bar">
      <n-button dashed size="small" @click="$router.push('/worker/route')">
        <template #icon><n-icon size="16"><MapOutline /></n-icon></template>
        规划路线
      </n-button>
    </div>
    <div class="category-tags">
      <n-tag v-for="cat in allCategories" :key="cat" :type="selectedCategory === cat ? 'primary' : 'default'"
        :checked="selectedCategory === cat" size="small" class="cat-tag" @click="onCategoryClick(cat)">
        {{ cat === '全部' ? '全部' : getCategoryIcon(cat) + ' ' + cat }}
      </n-tag>
    </div>

    <n-tabs v-model:value="tab" type="line" @update:value="onTabChange">
      <n-tab-pane name="all" tab="全部" />
      <n-tab-pane name="assigned" tab="待接单" />
      <n-tab-pane name="in_progress" tab="进行中" />
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
        <div class="card-student">报修人：{{ o.student_name }}</div>
      </n-card>
    </div>
    <n-empty v-else description="暂无工单" style="margin-top:80px" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import { CATEGORIES, getCategoryIcon } from '../../composables/useCategories.js'
import StatusBadge from '../../components/StatusBadge.vue'
import { MapOutline } from '@vicons/ionicons5'

const router = useRouter()
const store = useOrdersStore()
const tab = ref('all')
const orders = ref([])
const selectedCategory = ref('')
const allCategories = computed(() => ['全部', ...CATEGORIES])

async function load(status) {
  await store.fetchOrders(status || null, selectedCategory.value || undefined)
  orders.value = store.orders
}

function onCategoryClick(cat) {
  selectedCategory.value = cat === '全部' ? '' : cat
  load(tab.value === 'all' ? null : tab.value)
}
function onTabChange(val) { load(val === 'all' ? null : val) }
function goOrder(id) { router.push(`/worker/order/${id}`) }
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
.route-btn-bar {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}
.category-tags {
  display: flex;
  gap: 8px;
  margin: 0 0 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  flex-wrap: wrap;
}
.category-tags::-webkit-scrollbar { display: none; }
.cat-tag { cursor: pointer; flex-shrink: 0; }
.order-list { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
.order-card { border-radius: 12px; }
.card-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.card-time { font-size: 12px; color: #aaa; }
.card-title { font-size: 15px; font-weight: 600; color: #333; }
.card-desc { font-size: 13px; color: #888; margin-top: 4px; }
.card-student { font-size: 12px; color: #999; margin-top: 4px; }

@media (min-width: 768px) {
  .page-content { padding: 0; }
  .order-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
}
</style>
