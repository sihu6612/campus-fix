<template>
  <div class="page">
    <n-layout>
      <n-layout-header bordered class="app-header">
        <div class="header-inner">
          <n-button text @click="$router.back()"><n-icon size="20"><ArrowBackOutline /></n-icon></n-button>
          <h2>新建报修</h2>
          <div style="width:36px"></div>
        </div>
      </n-layout-header>

      <n-layout-content class="app-content">
        <n-form ref="formRef" :model="form" label-placement="top">
          <n-form-item label="报修类型">
            <n-select v-model:value="form.category" placeholder="选择类型" :options="catOpts" />
          </n-form-item>
          <n-form-item label="具体位置">
            <n-input v-model:value="form.location" placeholder="如：教学楼A 301室" clearable />
          </n-form-item>
          <n-form-item label="问题描述">
            <n-input v-model:value="form.description" type="textarea" placeholder="请描述具体问题..." :autosize="{ minRows: 3 }" />
          </n-form-item>
          <n-form-item label="现场照片">
            <ImageUpload auto-analyze :label="'拍照或上传'"
              @uploaded="url => form.image_urls = url ? [url] : []"
              @analyzed="onAnalyzed" />
          </n-form-item>
          <n-form-item v-if="form.ai_analysis" label="AI 分析结果">
            <n-card size="small" :bordered="true" style="background:#f8f7ff">
              <div><n-tag type="info" size="small">{{ form.ai_analysis.category }}</n-tag> {{ form.ai_analysis.worker_type }}</div>
              <div style="margin-top:4px;font-size:13px;color:#666">
                难度：{{ cpxMap[form.ai_analysis.complexity] || form.ai_analysis.complexity }}
                · 紧急：{{ form.urgency === 'urgent' ? '紧急' : '普通' }}
              </div>
            </n-card>
          </n-form-item>
          <n-form-item label="紧急程度">
            <n-radio-group v-model:value="form.urgency">
              <n-radio value="normal">普通</n-radio>
              <n-radio value="urgent">紧急</n-radio>
            </n-radio-group>
          </n-form-item>
        </n-form>
      </n-layout-content>
    </n-layout>

    <div class="submit-bar safe-bottom">
      <n-button type="primary" block size="large" :loading="submitting" @click="submit">提交报修</n-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { ArrowBackOutline } from '@vicons/ionicons5'
import { useOrdersStore } from '../../stores/orders.js'
import ImageUpload from '../../components/ImageUpload.vue'

const router = useRouter()
const message = useMessage()
const store = useOrdersStore()
const submitting = ref(false)

const catOpts = [
  { label: '电路/灯具', value: '电路/灯具' }, { label: '供水/管道', value: '供水/管道' },
  { label: '家具/门窗', value: '家具/门窗' }, { label: '空调/电器', value: '空调/电器' },
  { label: '网络/弱电', value: '网络/弱电' }, { label: '墙面/渗水', value: '墙面/渗水' },
  { label: '锁具/五金', value: '锁具/五金' }, { label: '卫生/下水', value: '卫生/下水' },
  { label: '其它', value: '其它' },
]

const cpxMap = { simple: '简单', medium: '中等', complex: '复杂' }

const form = ref({
  category: '', location: '', description: '', image_urls: [],
  urgency: 'normal', ai_analysis: null, suggested_parts: [], complexity: 'simple',
})

function onAnalyzed(analysis) {
  if (!analysis) return
  form.value.ai_analysis = analysis
  form.value.category = analysis.category || form.value.category
  form.value.complexity = analysis.complexity || 'simple'
  form.value.suggested_parts = analysis.suggested_parts || []
  if (analysis.urgency === 'urgent') form.value.urgency = 'urgent'
}

async function submit() {
  if (!form.value.category || !form.value.location || !form.value.description) {
    message.warning('请填写类型、位置和描述')
    return
  }
  submitting.value = true
  try {
    await store.createOrder(form.value)
    message.success('报修提交成功！')
    router.push('/student')
  } catch (e) {
    message.error(e.message || '提交失败')
  }
  submitting.value = false
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; }
.app-header { padding: 0 16px; }
.header-inner { display: flex; justify-content: space-between; align-items: center; height: 56px; }
.header-inner h2 { font-size: 18px; }
.app-content { flex: 1; overflow-y: auto; padding: 16px; }
.submit-bar { position: fixed; bottom: 0; width: 100%; padding: 12px 16px; background: #fff; border-top: 1px solid #eee; z-index: 10; }
</style>
