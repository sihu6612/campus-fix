<template>
  <div class="image-upload">
    <div v-if="imageUrl" class="preview">
      <img :src="imageUrl" alt="预览" />
      <n-button size="tiny" circle type="error" class="remove-btn" @click="remove">×</n-button>
    </div>
    <n-upload
      v-else
      :show-file-list="false"
      accept="image/*"
      :max="1"
      @change="handleChange"
      :custom-request="() => {}"
    >
      <n-button dashed>
        <template #icon><n-icon><CameraOutline /></n-icon></template>
        {{ label }}
      </n-button>
    </n-upload>
    <div v-if="analyzing" class="analyzing"><n-spin size="small" /> AI 分析中...</div>
    <div v-if="analysis" class="analysis-result">
      <n-tag size="small" type="info" round>{{ analysis.category || '未识别' }}</n-tag>
      <span class="analysis-detail">{{ analysis.worker_type }} · {{ complexityLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { CameraOutline } from '@vicons/ionicons5'
import { useOrdersStore } from '../stores/orders.js'

const props = defineProps({
  label: { type: String, default: '上传图片' },
  autoAnalyze: { type: Boolean, default: false },
})

const emit = defineEmits(['uploaded', 'analyzed'])
const store = useOrdersStore()
const imageUrl = ref('')
const analyzing = ref(false)
const analysis = ref(null)

const complexityLabel = {
  simple: '简单', medium: '中等', complex: '复杂',
}

function compressImage(file) {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      const maxW = 512
      const scale = Math.min(1, maxW / img.width)
      const w = Math.round(img.width * scale)
      const h = Math.round(img.height * scale)
      const canvas = document.createElement('canvas')
      canvas.width = w
      canvas.height = h
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, w, h)
      canvas.toBlob((blob) => {
        const reader = new FileReader()
        reader.onloadend = () => resolve(reader.result)
        reader.readAsDataURL(blob)
      }, 'image/jpeg', 0.7)
    }
    img.src = URL.createObjectURL(file)
  })
}

async function handleChange({ file }) {
  if (!file.file) return
  try {
    if (props.autoAnalyze) {
      analyzing.value = true
      const base64 = await compressImage(file.file)
      const res = await store.analyzeImageFast(base64)
      imageUrl.value = res.url
      analysis.value = res.analysis
      emit('uploaded', res.url)
      emit('analyzed', res.analysis)
    } else {
      imageUrl.value = await store.uploadImage(file.file)
      emit('uploaded', imageUrl.value)
    }
  } catch (e) {
    // ignore
  }
  analyzing.value = false
}

function remove() {
  imageUrl.value = ''
  analysis.value = null
  emit('uploaded', '')
  emit('analyzed', null)
}
</script>

<style scoped>
.image-upload { display: flex; flex-direction: column; gap: 8px; align-items: flex-start; }
.preview { position: relative; display: inline-block; }
.preview img { width: 120px; height: 120px; object-fit: cover; border-radius: 8px; }
.remove-btn { position: absolute; top: -6px; right: -6px; }
.analyzing { font-size: 12px; color: #999; display: flex; align-items: center; gap: 4px; }
.analysis-result { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #666; }
</style>
