import { ref, onMounted, onUnmounted } from 'vue'

const MOBILE_BREAKPOINT = 768

const isMobile = ref(window.innerWidth < MOBILE_BREAKPOINT)
let mql = null

function onMatch(e) {
  isMobile.value = !e.matches
}

export function useScreen() {
  onMounted(() => {
    mql = window.matchMedia(`(min-width: ${MOBILE_BREAKPOINT}px)`)
    mql.addEventListener('change', onMatch)
  })

  onUnmounted(() => {
    if (mql) mql.removeEventListener('change', onMatch)
  })

  return { isMobile }
}
