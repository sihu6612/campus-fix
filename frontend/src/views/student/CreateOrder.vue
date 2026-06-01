<template>
  <div class="page-content">
    <n-form ref="formRef" :model="form" label-placement="top">
      <n-form-item label="报修类型" required :feedback="errors.category">
        <n-select v-model:value="form.category" placeholder="选择类型" :options="catOpts" :status="errors.category ? 'error' : undefined" />
      </n-form-item>
      <n-form-item label="具体位置" required :feedback="errors.location">
        <n-input v-model:value="form.location" placeholder="如：教学楼A 301室" clearable :status="errors.location ? 'error' : undefined" />
      </n-form-item>
      <n-form-item label="问题描述" required :feedback="errors.description">
        <n-input v-model:value="form.description" type="textarea" placeholder="请描述具体问题..."
          :autosize="{ minRows: 3, maxRows: 6 }" :status="errors.description ? 'error' : undefined" show-count />
      </n-form-item>
      <n-form-item label="现场照片">
        <ImageUpload auto-analyze :label="'拍照或上传'"
          @uploaded="url => form.image_urls = url ? [url] : []"
          @analyzed="onAnalyzed" />
      </n-form-item>
      <n-form-item v-if="analyzing" label="AI 分析">
        <div class="skeleton-card"><div class="skeleton skeleton-line w80"></div><div class="skeleton skeleton-line w60" style="margin-top:8px;height:12px"></div></div>
      </n-form-item>
      <n-form-item v-else-if="form.ai_analysis" label="AI 分析结果">
        <n-card size="small" :bordered="true" style="background:#f8f7ff">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
            <n-tag type="info" size="small">{{ form.ai_analysis.category }}</n-tag>
            <span style="font-size:14px;color:#333">{{ form.ai_analysis.description }}</span>
          </div>
          <div style="font-size:13px;color:#666">
            难度：{{ cpxMap[form.ai_analysis.complexity] || form.ai_analysis.complexity }}
            · 紧急：{{ form.urgency === 'urgent' ? '紧急' : '普通' }}
            · 配件：{{ form.ai_analysis.suggested_parts?.join('、') || '无' }}
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

    <div class="submit-bar safe-bottom">
      <n-button type="primary" block size="large" :loading="submitting" @click="submit">
        <template #default>{{ submitting ? '提交中...' : '提交报修' }}</template>
      </n-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { useOrdersStore } from '../../stores/orders.js'
import ImageUpload from '../../components/ImageUpload.vue'

const router = useRouter()
const message = useMessage()
const store = useOrdersStore()
const submitting = ref(false)
const analyzing = ref(false)

import { CATEGORIES } from '../../composables/useCategories.js'
const catOpts = CATEGORIES.map(c => ({ label: c, value: c }))

const cpxMap = { simple: '简单', medium: '中等', complex: '复杂' }

const form = ref({
  category: '', location: '', description: '', image_urls: [],
  urgency: 'normal', urgency_score: 0, ai_analysis: null, suggested_parts: [], complexity: 'simple',
})

const errors = reactive({ category: '', location: '', description: '' })

function clearErrors() {
  errors.category = ''
  errors.location = ''
  errors.description = ''
}

function onAnalyzed(analysis) {
  if (!analysis) return
  form.value.ai_analysis = analysis
  form.value.category = analysis.category || form.value.category
  form.value.description = analysis.description || form.value.description
  form.value.complexity = analysis.complexity || 'simple'
  form.value.suggested_parts = analysis.suggested_parts || []
  if (analysis.urgency === 'urgent') form.value.urgency = 'urgent'
  form.value.urgency_score = analysis.urgency_score || 0
}

async function submit() {
  clearErrors()
  let valid = true
  if (!form.value.category) { errors.category = '请选择报修类型'; valid = false }
  if (!form.value.location.trim()) { errors.location = '请填写具体位置'; valid = false }
  if (!form.value.description.trim()) { errors.description = '请描述具体问题'; valid = false }
  if (!valid) return

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
.page-content {
  padding: 16px 16px 100px;
}

.submit-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #eee;
  z-index: 10;
}

@media (min-width: 768px) {
  .page-content {
    max-width: 720px;
    padding: 0 0 80px;
  }
  .submit-bar {
    position: static;
    padding: 16px 0 0;
    border: none;
    background: transparent;
  }
}
</style>
