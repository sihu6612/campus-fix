<template>
  <div class="page-content" ref="pageRef">
    <!-- 下拉刷新提示 -->
    <div class="pull-indicator" :class="{ releasing: pulling > 60, active: refreshing }" :style="{ height: pulling + 'px' }">
      <n-icon size="18" :class="{ spinning: refreshing }"><RefreshOutline /></n-icon>
      <span>{{ refreshing ? '刷新中...' : pulling > 60 ? '松开刷新' : '下拉刷新' }}</span>
    </div>

    <n-tabs v-model:value="tab" type="line" @update:value="onTabChange">
      <n-tab-pane name="all" tab="全部" />
      <n-tab-pane name="pending" tab="待分配" />
      <n-tab-pane name="in_progress" tab="维修中" />
      <n-tab-pane name="awaiting_confirmation" tab="待确认" />
      <n-tab-pane name="completed" tab="已完成" />
    </n-tabs>

    <!-- 加载中：骨架屏 -->
    <div v-if="loading" class="order-list">
      <div v-for="i in 3" :key="i" class="skeleton-card">
        <div class="skeleton skeleton-line w40" style="height:20px"></div>
        <div class="skeleton skeleton-line w80" style="margin-top:10px"></div>
        <div class="skeleton skeleton-line w60" style="height:12px;margin-top:8px"></div>
      </div>
    </div>

    <!-- 工单列表 -->
    <div v-else-if="orders.length" class="order-list">
      <n-card v-for="o in orders" :key="o.id" size="small" class="order-card" hoverable @click="goOrder(o.id)">
        <div class="card-row">
          <StatusBadge :status="o.status" />
          <span class="card-time">{{ fmtTime(o.created_at) }}</span>
        </div>
        <div class="card-title">
          <span class="cat-icon">{{ catIcon(o.category) }}</span>
          {{ o.category }}
        </div>
        <div class="card-desc">{{ o.description.slice(0, 60) }}{{ o.description.length > 60 ? '...' : '' }}</div>
        <div class="card-meta">
          <n-icon size="14"><LocationOutline /></n-icon>
          <span>{{ o.location }}</span>
        </div>
      </n-card>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <n-icon size="64" color="#d0d0d0"><FileTrayOutline /></n-icon>
      <p class="empty-title">暂无报修工单</p>
      <p class="empty-desc">点击下方按钮发起新的报修吧~</p>
    </div>

    <!-- 浮动按钮 -->
    <div v-show="!agentPanelOpen" class="fab">
      <n-button type="primary" circle size="large" @click="$router.push('/student/create')">
        <template #icon><n-icon size="24"><AddOutline /></n-icon></template>
      </n-button>
    </div>

    <!-- 底部 TabBar -->
    <div class="bottom-tabbar safe-bottom">
      <div class="tab-item active"><n-icon size="22"><ListOutline /></n-icon><span>工单</span></div>
      <div class="tab-item" @click="$router.push('/student/create')"><n-icon size="22"><AddCircleOutline /></n-icon><span>报修</span></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AddOutline, ListOutline, AddCircleOutline, RefreshOutline, FileTrayOutline, LocationOutline } from '@vicons/ionicons5'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import { agentPanelOpen } from '../../composables/useAgent.js'
import StatusBadge from '../../components/StatusBadge.vue'

const router = useRouter()
const store = useOrdersStore()
const tab = ref('all')
const orders = ref([])
const loading = ref(true)
const refreshing = ref(false)
const pulling = ref(0)
const pageRef = ref(null)

const catIconMap = {
  '电路/灯具': '💡', '供水/管道': '🚿', '家具/门窗': '🪟', '空调/电器': '❄️',
  '网络/弱电': '📶', '墙面/渗水': '🧱', '锁具/五金': '🔑', '卫生/下水': '🚽',
}
function catIcon(cat) { return catIconMap[cat] || '🔧' }

async function loadOrders(status) {
  loading.value = true
  try {
    await store.fetchOrders(status || undefined)
    orders.value = store.orders
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onTabChange(val) {
  loadOrders(val === 'all' ? null : val)
}

function goOrder(id) { router.push(`/student/order/${id}`) }
function fmtTime(t) { return t ? new Date(t).toLocaleDateString('zh-CN') : '' }

// 下拉刷新：触摸事件
let startY = 0
function onTouchStart(e) {
  if (pageRef.value.scrollTop <= 0) startY = e.touches[0].clientY
}
function onTouchMove(e) {
  if (startY === 0) return
  const dy = e.touches[0].clientY - startY
  if (dy > 0) {
    pulling.value = Math.min(dy, 120)
    if (dy > 20) e.preventDefault()
  }
}
async function onTouchEnd() {
  if (pulling.value > 60 && !refreshing.value) {
    refreshing.value = true
    await loadOrders(tab.value === 'all' ? null : tab.value)
  }
  startY = 0
  pulling.value = 0
}

onMounted(() => {
  const el = pageRef.value
  if (el) {
    el.addEventListener('touchstart', onTouchStart, { passive: true })
    el.addEventListener('touchmove', onTouchMove, { passive: false })
    el.addEventListener('touchend', onTouchEnd)
  }
  loadOrders()
  subscribeOrders(() => loadOrders(tab.value === 'all' ? null : tab.value))
})
</script>

<style scoped>
.page-content {
  padding: 0 16px 80px;
  min-height: 100vh;
}

/* 下拉刷新 */
.pull-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 0;
  overflow: hidden;
  color: #999;
  font-size: 13px;
  transition: height 0.2s;
}
.pull-indicator.releasing { color: #4f46e5; }
.pull-indicator.active { color: #4f46e5; }
.spinning { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.order-card {
  border-radius: 12px;
  transition: transform 0.15s;
}
.order-card:active { transform: scale(0.98); }

.card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.card-time { font-size: 12px; color: #aaa; }

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 6px;
}
.cat-icon { font-size: 16px; }

.card-desc {
  font-size: 13px;
  color: #888;
  margin-top: 6px;
  line-height: 1.4;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  font-size: 12px;
  color: #aaa;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px 0;
}
.empty-title {
  font-size: 16px;
  color: #999;
  margin-top: 16px;
}
.empty-desc {
  font-size: 13px;
  color: #bbb;
  margin-top: 6px;
}

.fab {
  position: fixed;
  bottom: 140px;
  right: 20px;
  z-index: 10;
}

.bottom-tabbar {
  display: flex;
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #fff;
  border-top: 1px solid #f0f0f0;
  z-index: 20;
}
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  color: #999;
  cursor: pointer;
  font-size: 11px;
  gap: 2px;
}
.tab-item.active { color: #4f46e5; }

@media (min-width: 768px) {
  .page-content {
    padding: 0 0 40px;
    min-height: auto;
  }
  .order-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  .fab {
    right: 32px;
    bottom: 32px;
  }
  .bottom-tabbar { display: none; }
  .pull-indicator { display: none; }
}
</style>
