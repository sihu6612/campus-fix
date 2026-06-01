<template>
  <div class="page-content" ref="pageRef">
    <!-- 下拉刷新提示 -->
    <div class="pull-indicator" :class="{ releasing: pulling > 60, active: refreshing }" :style="{ height: pulling + 'px' }">
      <n-icon size="18" :class="{ spinning: refreshing }"><RefreshOutline /></n-icon>
      <span>{{ refreshing ? '刷新中...' : pulling > 60 ? '松开刷新' : '下拉刷新' }}</span>
    </div>

    <!-- 补填班级提示（存量学生 class_name 为空时显示） -->
    <div v-if="showClassPrompt" class="class-prompt">
      <n-icon size="18" color="#f0a020"><WarningOutline /></n-icon>
      <span>请完善你的班级信息，以便辅导员查看你的工单</span>
      <n-input v-model:value="classInput" placeholder="如：软件工程2101" size="small" class="class-input" />
      <n-button size="small" type="warning" :loading="savingClass" @click="saveClassName">保存</n-button>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { AddOutline, ListOutline, AddCircleOutline, RefreshOutline, FileTrayOutline, LocationOutline, WarningOutline } from '@vicons/ionicons5'
import { useOrdersStore } from '../../stores/orders.js'
import { useAuthStore } from '../../stores/auth.js'
import { supabase } from '../../composables/useSupabase.js'
import { subscribeOrders } from '../../composables/useRealtime.js'
import { agentPanelOpen } from '../../composables/useAgent.js'
import { CATEGORIES, getCategoryIcon } from '../../composables/useCategories.js'
import StatusBadge from '../../components/StatusBadge.vue'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()
const store = useOrdersStore()
const tab = ref('all')
const orders = ref([])
const loading = ref(true)
const refreshing = ref(false)
const pulling = ref(0)
const pageRef = ref(null)
const selectedCategory = ref('')
const allCategories = computed(() => ['全部', ...CATEGORIES])

// 班级补填
const classInput = ref('')
const savingClass = ref(false)
const showClassPrompt = computed(() => auth.role === 'student' && !auth.user?.class_name)

async function saveClassName() {
  if (!classInput.value.trim()) return
  savingClass.value = true
  try {
    await supabase.from('profiles').update({ class_name: classInput.value.trim() }).eq('id', auth.userId)
    auth.user.class_name = classInput.value.trim()
    localStorage.setItem('cf_user', JSON.stringify(auth.user))
    message.success('班级已保存')
  } catch (e) {
    message.error('保存失败')
  }
  savingClass.value = false
}

function catIcon(cat) { return getCategoryIcon(cat) }

async function loadOrders(status) {
  loading.value = true
  try {
    await store.fetchOrders(status || undefined, selectedCategory.value || undefined)
    orders.value = store.orders
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

function onCategoryClick(cat) {
  selectedCategory.value = cat === '全部' ? '' : cat
  loadOrders(tab.value === 'all' ? null : tab.value)
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

/* 班级补填提示 */
.class-prompt {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0 0;
  padding: 10px 12px;
  background: #fff8e6;
  border: 1px solid #ffe4a0;
  border-radius: 10px;
  font-size: 13px;
  color: #8a6d14;
  flex-wrap: wrap;
}
.class-prompt span {
  flex: 1 1 auto;
  min-width: 180px;
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

.class-input {
  width: 160px;
  flex-shrink: 0;
}

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
