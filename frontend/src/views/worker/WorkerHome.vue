<template>
  <div class="app-shell">
    <n-layout>
      <n-layout-header bordered class="app-header">
        <div class="header-inner">
          <h2>师傅工作台</h2>
          <n-dropdown :options="menuOpts" @select="handleMenu">
            <n-button text><n-icon size="24"><PersonCircleOutline /></n-icon></n-button>
          </n-dropdown>
        </div>
      </n-layout-header>

      <n-layout-content class="app-content">
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
      </n-layout-content>
    </n-layout>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PersonCircleOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../../stores/auth.js'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import StatusBadge from '../../components/StatusBadge.vue'

const router = useRouter()
const auth = useAuthStore()
const store = useOrdersStore()
const tab = ref('assigned')
const orders = ref([])

const menuOpts = [{ label: '退出登录', key: 'logout' }]

function handleMenu(key) {
  if (key === 'logout') { auth.logout(); router.push('/login') }
}

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
.card-student { font-size: 12px; color: #999; margin-top: 4px; }
</style>
