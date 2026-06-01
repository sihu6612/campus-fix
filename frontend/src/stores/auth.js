import { defineStore } from 'pinia'
import { supabase } from '../composables/useSupabase.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('cf_user') || 'null'),
    session: JSON.parse(localStorage.getItem('cf_session') || 'null'),
  }),
  getters: {
    isLoggedIn: (state) => !!state.session,
    role: (state) => state.user?.role || 'student',
    userId: (state) => state.user?.id || '',
  },
  actions: {
    async login(email, password) {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) throw error
      // 取 profile
      const { data: profile } = await supabase.from('profiles').select('*').eq('id', data.user.id).single()
      const user = { id: data.user.id, email: data.user.email, role: profile?.role || 'student', display_name: profile?.display_name || '', class_name: profile?.class_name || '' }
      this.user = user
      this.session = data.session
      localStorage.setItem('cf_user', JSON.stringify(user))
      localStorage.setItem('cf_session', JSON.stringify(data.session))
      return user
    },
    async register(email, password, displayName, role, className = '') {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { display_name: displayName, role, class_name: className } }
      })
      if (error) throw error
      return data
    },
    async adminRegister(email, password, displayName) {
      const res = await fetch(`${import.meta.env.VITE_API_BASE || ''}/api/auth/admin/register?secret=xiaoling2026`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, display_name: displayName, role: 'admin', class_name: '' }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: '注册失败' }))
        throw new Error(err.detail || '注册失败')
      }
      return res.json()
    },
    async logout() {
      await supabase.auth.signOut()
      this.user = null
      this.session = null
      localStorage.removeItem('cf_user')
      localStorage.removeItem('cf_session')
    },
  },
})
