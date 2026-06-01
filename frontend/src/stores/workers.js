import { defineStore } from 'pinia'
import { api } from '../composables/useSupabase.js'

export const useWorkersStore = defineStore('workers', {
  state: () => ({
    workers: [],
    suggestions: [],
    best: null,
  }),
  actions: {
    async fetchWorkers() {
      this.workers = await api('/api/workers/')
    },
    async suggestWorker(orderId) {
      const res = await api(`/api/workers/suggest?order_id=${orderId}`)
      this.suggestions = res.suggestions || []
      this.best = res.best || null
      return res
    },
  },
})
