import { defineStore } from 'pinia'
import { api } from '../composables/useSupabase.js'
import { useAuthStore } from './auth.js'

export const useOrdersStore = defineStore('orders', {
  state: () => ({
    orders: [],
    activeOrder: null,
    messages: [],
    logs: [],
  }),
  actions: {
    async fetchOrders(status, category, className) {
      const auth = useAuthStore()
      const params = new URLSearchParams({ user_id: auth.userId, role: auth.role })
      if (status) params.set('status', status)
      if (category) params.set('category', category)
      if (className) params.set('class_name', className)
      this.orders = await api(`/api/orders/?${params}`)
    },
    async fetchOrder(id) {
      this.activeOrder = await api(`/api/orders/${id}`)
    },
    async createOrder(data) {
      const auth = useAuthStore()
      return await api(`/api/orders/?student_id=${auth.userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
    },
    async updateOrder(id, data) {
      const result = await api(`/api/orders/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (this.activeOrder?.id === id) this.activeOrder = result
      return result
    },
    async cancelOrder(id) {
      await api(`/api/orders/${id}`, { method: 'DELETE' })
    },
    async hardDeleteOrder(id) {
      await api(`/api/orders/${id}?hard=true`, { method: 'DELETE' })
    },
    async batchUpdateOrders(orderIds, updates) {
      return await api('/api/orders/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_ids: orderIds, updates }),
      })
    },
    async fetchCategories() {
      const res = await api('/api/orders/categories')
      return res.categories
    },
    async fetchMessages(orderId) {
      this.messages = await api(`/api/messages/${orderId}`)
    },
    async sendMessage(orderId, content) {
      const auth = useAuthStore()
      await api(`/api/messages/?sender_id=${auth.userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_id: orderId, content }),
      })
    },
    async fetchLogs(orderId) {
      this.logs = await api(`/api/messages/${orderId}/logs`)
    },
    async uploadImage(file) {
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch(`${import.meta.env.VITE_API_BASE || ''}/api/upload/image`, { method: 'POST', body: fd })
      if (!res.ok) throw new Error('上传失败')
      const data = await res.json()
      return data.url
    },
    async analyzeImage(file) {
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch(`${import.meta.env.VITE_API_BASE || ''}/api/upload/analyze`, { method: 'POST', body: fd })
      if (!res.ok) throw new Error('分析失败')
      return await res.json()
    },
    async analyzeImageFast(base64) {
      const res = await api('/api/upload/analyze/fast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: base64 }),
      })
      return res
    },
  },
})
