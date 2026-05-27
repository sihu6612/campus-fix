<template>
  <div class="app-shell">
    <n-layout>
      <n-layout-header bordered class="app-header">
        <div class="header-inner">
          <h2>我的报修</h2>
          <n-dropdown :options="menuOpts" @select="handleMenu">
            <n-button text><n-icon size="24"><PersonCircleOutline /></n-icon></n-button>
          </n-dropdown>
        </div>
      </n-layout-header>

      <n-layout-content class="app-content">
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
          </n-card>
        </div>
        <n-empty v-else description="暂无报修" style="margin-top:80px" />
      </n-layout-content>
    </n-layout>

    <div class="fab">
      <n-button type="primary" circle size="large" @click="$router.push('/student/create')">
        <template #icon><n-icon size="24"><AddOutline /></n-icon></template>
      </n-button>
    </div>

    <n-layout-footer bordered class="app-tabbar safe-bottom">
      <div class="tab-item active"><n-icon size="22"><ListOutline /></n-icon><span>工单</span></div>
      <div class="tab-item" @click="$router.push('/student/create')"><n-icon size="22"><AddCircleOutline /></n-icon><span>报修</span></div>
    </n-layout-footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PersonCircleOutline, AddOutline, ListOutline, AddCircleOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../../stores/auth.js'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import StatusBadge from '../../components/StatusBadge.vue'

const router = useRouter()
const auth = useAuthStore()
const store = useOrdersStore()
const tab = ref('all')
const orders = ref([])

const menuOpts = [
  { label: '退出登录', key: 'logout' }
]

function handleMenu(key) {
  if (key === 'logout') { auth.logout(); router.push('/login') }
}

async function loadOrders(status) {
  await store.fetchOrders(status || undefined)
  orders.value = store.orders
}

function onTabChange(val) {
  loadOrders(val === 'all' ? null : val)
}

function goOrder(id) { router.push(`/student/order/${id}`) }
function fmtTime(t) { return t ? new Date(t).toLocaleDateString('zh-CN') : '' }

onMounted(() => {
  loadOrders()
  subscribeOrders(() => loadOrders(tab.value === 'all' ? null : tab.value))
})
</script>

<style scoped>
.app-shell { height: 100vh; display: flex; flex-direction: column; }
.app-header { padding: 0 16px; }
.header-inner { display: flex; justify-content: space-between; align-items: center; height: 56px; }
.header-inner h2 { font-size: 18px; }
.app-content { flex: 1; overflow-y: auto; padding: 0 16px 80px; }
.order-list { display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
.order-card { border-radius: 12px; }
.card-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.card-time { font-size: 12px; color: #aaa; }
.card-title { font-size: 15px; font-weight: 600; color: #333; }
.card-desc { font-size: 13px; color: #888; margin-top: 4px; }
.fab { position: fixed; bottom: 80px; right: 20px; z-index: 10; }
.app-tabbar { display: flex; position: fixed; bottom: 0; width: 100%; background: #fff; }
.tab-item { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 8px 0; color: #999; cursor: pointer; font-size: 11px; gap: 2px; }
.tab-item.active { color: #4f46e5; }
</style>
