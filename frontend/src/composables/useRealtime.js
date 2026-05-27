import { supabase } from './useSupabase.js'

export function subscribeOrders(onUpdate) {
  return supabase
    .channel('orders-channel')
    .on('postgres_changes',
      { event: '*', schema: 'public', table: 'repair_orders' },
      (payload) => onUpdate(payload)
    )
    .subscribe()
}

export function subscribeMessages(orderId, onNew) {
  return supabase
    .channel(`messages-${orderId}`)
    .on('postgres_changes',
      { event: 'INSERT', schema: 'public', table: 'repair_messages', filter: `order_id=eq.${orderId}` },
      (payload) => onNew(payload.new)
    )
    .subscribe()
}
