// 高德地图 JS API v2 动态加载 + 地图/标记/路线工具

let amapReady = false
let loadPromise = null

export function loadAmap() {
  if (amapReady) return Promise.resolve(window.AMap)
  if (loadPromise) return loadPromise

  // 高德 JS API Key（Web端）
  const key = import.meta.env.VITE_AMAP_KEY || window.__AMAP_KEY__ || ''
  if (!key) {
    return Promise.reject(new Error('请配置高德地图 JS API Key (VITE_AMAP_KEY)'))
  }

  loadPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${key}&plugin=AMap.Driving`
    script.onload = () => {
      amapReady = true
      resolve(window.AMap)
    }
    script.onerror = () => reject(new Error('高德地图加载失败'))
    document.head.appendChild(script)
  })
  return loadPromise
}

export function createMap(container, center = [116.397, 39.908]) {
  return new window.AMap.Map(container, {
    zoom: 12,
    center,
    resizeEnable: true,
  })
}

export function addMarker(map, lng, lat, label, isStart = false) {
  const content = document.createElement('div')
  content.style.cssText = `
    background:${isStart ? '#4f46e5' : '#f0a020'};
    color:#fff;padding:2px 6px;border-radius:10px;
    font-size:12px;white-space:nowrap;
    box-shadow:0 2px 6px rgba(0,0,0,.15);
  `
  content.textContent = label

  const marker = new window.AMap.Marker({
    position: [lng, lat],
    content,
    offset: new window.AMap.Pixel(0, -15),
  })
  map.add(marker)
  return marker
}

export function drawRoute(map, steps) {
  const path = []
  for (const step of steps) {
    if (!step.polyline) continue
    const pts = step.polyline.split(';').map(p => {
      const [lng, lat] = p.split(',').map(Number)
      return [lng, lat]
    })
    path.push(...pts)
  }

  if (path.length === 0) return null

  const polyline = new window.AMap.Polyline({
    path,
    strokeColor: '#4f46e5',
    strokeWeight: 5,
    strokeOpacity: 0.7,
    lineJoin: 'round',
  })
  map.add(polyline)
  map.setFitView([polyline])
  return polyline
}
