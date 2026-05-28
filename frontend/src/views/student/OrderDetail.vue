<template>
  <div class="page">
    <n-layout>
      <n-layout-header bordered class="app-header">
        <div class="header-inner">
          <n-button text @click="$router.back()"><n-icon size="20"><ArrowBackOutline /></n-icon></n-button>
          <h2>工单详情</h2>
          <StatusBadge v-if="order" :status="order.status" />
        </div>
      </n-layout-header>

      <n-layout-content class="app-content" v-if="order">
        <n-card size="small" title="基本信息">
          <n-descriptions label-placement="left" :column="1" size="small">
            <n-descriptions-item label="类型">{{ order.category }}</n-descriptions-item>
            <n-descriptions-item label="位置">{{ order.location }}</n-descriptions-item>
            <n-descriptions-item label="描述">{{ order.description }}</n-descriptions-item>
            <n-descriptions-item label="学生">{{ order.student_name }}</n-descriptions-item>
            <n-descriptions-item v-if="order.worker_name" label="师傅">{{ order.worker_name }}</n-descriptions-item>
          </n-descriptions>
        </n-card>

        <n-card v-if="logs.length" size="small" title="维修进度" style="margin-top:12px">
          <OrderTimeline :logs="logs" />
        </n-card>

        <n-card size="small" title="沟通记录" style="margin-top:12px">
          <ChatBox :messages="messages" :user-id="auth.userId" @send="onSend" />
        </n-card>

        <div v-if="order.status === 'awaiting_confirmation' && auth.role === 'student'" style="margin-top:12px">
          <n-space vertical>
            <n-button type="primary" block @click="$router.push(`/student/confirm/${order.id}`)">确认维修完成</n-button>
          </n-space>
        </div>
      </n-layout-content>
    </n-layout>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowBackOutline } from '@vicons/ionicons5'
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
let msgSub = null

async function load() {
  await store.fetchOrder(route.params.id)
  order.value = store.activeOrder
  await Promise.all([loadMessages(), loadLogs()])
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
.page { height: 100vh; display: flex; flex-direction: column; }
.app-header { padding: 0 16px; }
.header-inner { display: flex; justify-content: space-between; align-items: center; height: 56px; }
.header-inner h2 { font-size: 18px; }
.app-content { flex: 1; overflow-y: auto; padding: 16px 16px 24px; }

@media (min-width: 768px) {
  .page { background: #f0f2f5; }
  .app-header { padding: 0; }
  .header-inner { max-width: 720px; margin: 0 auto; padding: 0 16px; }
  .app-content { max-width: 720px; margin: 0 auto; padding: 24px 0; }
}
</style>
