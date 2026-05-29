<template>
  <div class="page-content" v-if="order">
    <n-card size="small" class="info-card">
      <div class="confirm-title">师傅已提交维修完成</div>
      <n-descriptions label-placement="left" :column="1" size="small">
        <n-descriptions-item label="类型">{{ order.category }}</n-descriptions-item>
        <n-descriptions-item label="位置">{{ order.location }}</n-descriptions-item>
        <n-descriptions-item label="师傅">{{ order.worker_name }}</n-descriptions-item>
      </n-descriptions>
    </n-card>

    <n-space vertical style="margin-top:24px">
      <n-button type="success" block size="large" :loading="loading" @click="confirm(true)">确认完成，去评价</n-button>
      <n-button type="warning" block size="large" @click="showReject = true">有问题，退回重修</n-button>
    </n-space>

    <n-modal v-model:show="showRating" preset="card" title="评价师傅">
      <div class="rating-area">
        <n-rate v-model:value="rating" size="large" :count="5" />
      </div>
      <n-input v-model:value="review" type="textarea" placeholder="写几句评价..." :autosize="{ minRows: 2 }" style="margin-top:12px" />
      <n-button type="primary" block :loading="loading" @click="submitRating" style="margin-top:16px">提交评价</n-button>
    </n-modal>

    <n-modal v-model:show="showReject" preset="card" title="退回维修">
      <n-input v-model:value="rejectNote" type="textarea" placeholder="请说明哪里没修好..." :autosize="{ minRows: 2 }" />
      <n-button type="warning" block :loading="loading" @click="confirm(false)" style="margin-top:16px">退回师傅重新处理</n-button>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useOrdersStore } from '../../stores/orders.js'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const store = useOrdersStore()
const order = ref(null)
const loading = ref(false)
const showRating = ref(false)
const showReject = ref(false)
const rating = ref(5)
const review = ref('')
const rejectNote = ref('')

async function confirm(ok) {
  if (ok) {
    showRating.value = true
    return
  }
  if (!rejectNote.value.trim()) { message.warning('请填写问题说明'); return }
  loading.value = true
  try {
    await store.updateOrder(route.params.id, { status: 'in_progress' })
    await store.sendMessage(route.params.id, `[退回] ${rejectNote.value}`)
    message.success('已退回师傅')
    router.push(`/student/order/${route.params.id}`)
  } catch (e) {
    message.error(e.message)
  }
  loading.value = false
}

async function submitRating() {
  loading.value = true
  try {
    await store.updateOrder(route.params.id, { status: 'completed', rating: rating.value, review: review.value })
    message.success('评价已提交，工单已完成！')
    router.push('/student')
  } catch (e) {
    message.error(e.message)
  }
  loading.value = false
}

onMounted(async () => {
  await store.fetchOrder(route.params.id)
  order.value = store.activeOrder
})
</script>

<style scoped>
.page-content {
  padding: 16px;
}
.confirm-title { font-size: 16px; font-weight: 600; color: #16a34a; margin-bottom: 12px; text-align: center; }
.rating-area { display: flex; justify-content: center; padding: 16px; }

@media (min-width: 768px) {
  .page-content {
    max-width: 600px;
    padding: 0;
  }
}
</style>
