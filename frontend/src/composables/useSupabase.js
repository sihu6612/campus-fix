import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

let apiBase = import.meta.env.VITE_API_BASE || ''

export async function api(path, options = {}) {
  const session = JSON.parse(localStorage.getItem('cf_session') || 'null')
  const url = `${apiBase}${path}`
  const headers = { ...options.headers }
  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`
  }
  const res = await fetch(url, { ...options, headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: '请求失败' }))
    throw new Error(err.detail || '请求失败')
  }
  return res.json()
}
