<template>
  <div class="page-content">
    <n-tabs v-model:value="tab" type="line" @update:value="onTabChange">
      <n-tab-pane name="assigned" tab="待接单" />
      <n-tab-pane name="in_progress" tab="进行中" />
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
        <div class="card-student">报修人：{{ o.student_name }}</div>
      </n-card>
    </div>
    <n-empty v-else description="暂无工单" style="margin-top:80px" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import StatusBadge from '../../components/StatusBadge.vue'

const router = useRouter()
const store = useOrdersStore()
const tab = ref('assigned')
const orders = ref([])

async function load(status) {
  await store.fetchOrders(status)
  orders.value = store.orders
}

function onTabChange(val) { load(val) }
function goOrder(id) { router.push(`/worker/order/${id}`) }
function fmtTime(t) { return t ? new Date(t).toLocaleDateString('zh-CN') : '' }

onMounted(() => {
  load('assigned')
  subscribeOrders(() => load(tab.value))
})
</script>

<style scoped>
.page-content {
  padding: 0 16px 32px;
}
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
