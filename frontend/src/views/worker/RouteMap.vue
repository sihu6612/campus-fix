<template>
  <div class="route-page">
    <div class="route-header">
      <n-button size="small" @click="$router.back()">
        <template #icon><n-icon size="18"><ArrowBackOutline /></n-icon></template>
      </n-button>
      <span class="route-title">维修路线规划</span>
      <n-button size="small" type="primary" @click="refreshRoute" :loading="loading">刷新</n-button>
    </div>

    <div v-if="error" class="route-error">
      <n-icon size="48" color="#ccc"><MapOutline /></n-icon>
      <p>{{ error }}</p>
    </div>

    <div v-else ref="mapContainer" class="map-container"></div>

    <div v-if="routeData" class="route-info">
      <div class="route-summary">
        <span>总距离：{{ (routeData.route.distance / 1000).toFixed(1) }} 公里</span>
        <span>预计耗时：{{ Math.round(routeData.route.duration / 60) }} 分钟</span>
      </div>
      <div class="stop-list">
        <div v-for="m in routeData.route.markers" :key="m.order_id" class="stop-item">
          <span class="stop-index">{{ m.index }}</span>
          <span class="stop-name">{{ m.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowBackOutline, MapOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../../stores/auth.js'
import { api } from '../../composables/useSupabase.js'
import { loadAmap, createMap, addMarker, drawRoute } from '../../composables/useAmap.js'

const router = useRouter()
const auth = useAuthStore()
const mapContainer = ref(null)
const routeData = ref(null)
const loading = ref(false)
const error = ref('')

async function refreshRoute() {
  loading.value = true
  error.value = ''
  try {
    routeData.value = await api(`/api/workers/${auth.userId}/route`)
    if (!routeData.value?.route) {
      error.value = routeData.value?.message || '暂无可用路线数据'
    }
  } catch (e) {
    error.value = e.message || '路线加载失败'
  }
  loading.value = false
  if (routeData.value?.route) {
    await nextTick()
    renderMap()
  }
}

async function renderMap() {
  if (!mapContainer.value || !routeData.value?.route) return
  try {
    const AMap = await loadAmap()
    const r = routeData.value.route
    const map = createMap(mapContainer.value, [routeData.value.origin.lng, routeData.value.origin.lat])

    // 起点标记
    addMarker(map, routeData.value.origin.lng, routeData.value.origin.lat, '起点', true)

    // 途经点标记
    for (const m of r.markers) {
      addMarker(map, m.lng, m.lat, `${m.index}. ${m.name}`, false)
    }

    // 路线
    if (r.steps?.length) {
      drawRoute(map, r.steps)
    }
  } catch (e) {
    error.value = e.message || '地图渲染失败'
  }
}

onMounted(async () => {
  await refreshRoute()
})
</script>

<style scoped>
.route-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fff;
}
.route-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  z-index: 10;
}
.route-title {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
}
.map-container {
  flex: 1;
  min-height: 300px;
}
.route-error {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 14px;
  gap: 12px;
}
.route-info {
  background: #fff;
  border-top: 1px solid #f0f0f0;
  padding: 12px 16px 16px;
}
.route-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}
.stop-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.stop-list::-webkit-scrollbar { display: none; }
.stop-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: #f5f3ff;
  border-radius: 8px;
  white-space: nowrap;
  font-size: 13px;
}
.stop-index {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #4f46e5;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}
.stop-name {
  color: #333;
}
</style>
