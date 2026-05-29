<template>
  <div class="page-content">
    <!-- 骨架屏加载 -->
    <template v-if="loading">
      <div class="skeleton-card">
        <div class="skeleton skeleton-line w60" style="height:20px"></div>
        <div class="skeleton skeleton-line w80" style="margin-top:12px"></div>
        <div class="skeleton skeleton-line w40" style="margin-top:10px;height:12px"></div>
      </div>
      <div class="skeleton-card" style="margin-top:12px">
        <div class="skeleton skeleton-line w40" style="height:18px"></div>
        <div class="skeleton skeleton-line w80" style="margin-top:10px;height:12px"></div>
      </div>
    </template>

    <template v-else-if="order">
      <n-card size="small" title="基本信息">
        <n-descriptions label-placement="left" :column="1" size="small">
          <n-descriptions-item label="类型">{{ order.category }}</n-descriptions-item>
          <n-descriptions-item label="位置">{{ order.location }}</n-descriptions-item>
          <n-descriptions-item label="描述">{{ order.description }}</n-descriptions-item>
          <n-descriptions-item label="学生">{{ order.student_name }}</n-descriptions-item>
          <n-descriptions-item v-if="order.worker_name" label="维修师傅">{{ order.worker_name }}</n-descriptions-item>
          <n-descriptions-item label="状态">
            <StatusBadge :status="order.status" />
          </n-descriptions-item>
        </n-descriptions>
      </n-card>

      <n-card v-if="logs.length" size="small" title="维修进度" style="margin-top:12px">
        <OrderTimeline :logs="logs" />
      </n-card>

      <n-card size="small" title="沟通记录" style="margin-top:12px;margin-bottom:12px">
        <ChatBox :messages="messages" :user-id="auth.userId" @send="onSend" />
      </n-card>

      <div v-if="order.status === 'awaiting_confirmation' && auth.role === 'student'" style="margin-top:16px">
        <n-button type="primary" block size="large" @click="$router.push(`/student/confirm/${order.id}`)">
          确认维修完成
        </n-button>
      </div>
    </template>

    <n-empty v-else description="工单未找到" style="margin-top:80px" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth.js'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeMessages } from '../../composables/useRealtime.js'
import StatusBadge from '../../components/StatusBadge.vue'
import OrderTimeline from '../../components/OrderTimeline.vue'
import ChatBox from '../../components/ChatBox.vue'

const route = useRoute()
const auth = useAuthStore()
const store = useOrdersStore()
const order = ref(null)
const messages = ref([])
const logs = ref([])
const loading = ref(true)
let msgSub = null

async function load() {
  loading.value = true
  try {
    await store.fetchOrder(route.params.id)
    order.value = store.activeOrder
    await Promise.all([loadMessages(), loadLogs()])
  } finally {
    loading.value = false
  }
}

async function loadMessages() {
  await store.fetchMessages(route.params.id)
  messages.value = store.messages
}
async function loadLogs() {
  await store.fetchLogs(route.params.id)
  logs.value = store.logs
}
async function onSend(text) {
  await store.sendMessage(route.params.id, text)
  await loadMessages()
}

onMounted(() => {
  load()
  msgSub = subscribeMessages(route.params.id, () => loadMessages())
})
onUnmounted(() => { if (msgSub) msgSub.unsubscribe() })
</script>

<style scoped>
.page-content {
  padding: 16px 16px 24px;
}

@media (min-width: 768px) {
  .page-content {
    max-width: 800px;
    padding: 0;
  }
}
</style>
