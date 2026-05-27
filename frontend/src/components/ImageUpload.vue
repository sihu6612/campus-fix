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

async function handleChange({ file }) {
  if (!file.file) return
  try {
    if (props.autoAnalyze) {
      analyzing.value = true
      const res = await store.analyzeImage(file.file)
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
