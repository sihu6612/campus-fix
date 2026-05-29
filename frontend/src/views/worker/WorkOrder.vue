<template>
  <div class="page-content" v-if="order">
    <n-card size="small" title="报修信息">
      <n-descriptions label-placement="left" :column="1" size="small">
        <n-descriptions-item label="类型">{{ order.category }}</n-descriptions-item>
        <n-descriptions-item label="位置">{{ order.location }}</n-descriptions-item>
        <n-descriptions-item label="描述">{{ order.description }}</n-descriptions-item>
        <n-descriptions-item label="学生">{{ order.student_name }}</n-descriptions-item>
        <n-descriptions-item v-if="order.suggested_parts?.length" label="建议配件">
          {{ order.suggested_parts.join('、') }}
        </n-descriptions-item>
      </n-descriptions>
      <div v-if="order.image_urls?.length" style="margin-top:8px">
        <img v-for="url in order.image_urls" :key="url" :src="url" style="width:80px;height:80px;object-fit:cover;border-radius:8px;margin-right:8px" />
      </div>
    </n-card>

    <n-space vertical style="margin-top:16px">
      <n-button v-if="order.status === 'assigned'" type="primary" block size="large" :loading="loading" @click="acceptOrder">确认接单</n-button>
      <n-button v-if="order.status === 'in_progress'" type="primary" block size="large" :loading="loading" @click="submitComplete">提交完工</n-button>
    </n-space>

    <n-modal v-model:show="showComplete" preset="card" title="提交完工">
      <n-input v-model:value="completeNote" type="textarea" placeholder="维修说明..." :autosize="{ minRows: 2 }" />
      <n-button type="primary" block :loading="loading" @click="doComplete" style="margin-top:16px">确认完工</n-button>
    </n-modal>

    <n-card size="small" title="沟通记录" style="margin-top:12px">
      <ChatBox :messages="messages" :user-id="auth.userId" @send="onSend" />
    </n-card>

    <n-card v-if="logs.length" size="small" title="进度记录" style="margin-top:12px">
      <OrderTimeline :logs="logs" />
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useAuthStore } from '../../stores/auth.js'
import { useOrdersStore } from '../../stores/orders.js'
import { subscribeMessages } from '../../composables/useRealtime.js'
import StatusBadge from '../../components/StatusBadge.vue'
import OrderTimeline from '../../components/OrderTimeline.vue'
import ChatBox from '../../components/ChatBox.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const auth = useAuthStore()
const store = useOrdersStore()
const order = ref(null)
const messages = ref([])
const logs = ref([])
const loading = ref(false)
const showComplete = ref(false)
const completeNote = ref('')
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

async function acceptOrder() {
  loading.value = true
  try {
    await store.updateOrder(route.params.id, { status: 'in_progress' })
    await store.sendMessage(route.params.id, '我已接单，马上处理。')
    message.success('已接单')
    load()
  } catch (e) { message.error(e.message) }
  loading.value = false
}

function submitComplete() { showComplete.value = true }

async function doComplete() {
  loading.value = true
  try {
    await store.updateOrder(route.params.id, { status: 'awaiting_confirmation' })
    await store.sendMessage(route.params.id, `维修完成：${completeNote.value || '已处理完毕，请确认。'}`)
    message.success('已提交完工，等待学生确认')
    showComplete.value = false
    load()
  } catch (e) { message.error(e.message) }
  loading.value = false
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
