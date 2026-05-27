<template>
  <div class="chat-box">
    <div class="chat-messages" ref="msgList">
      <div v-for="m in messages" :key="m.id" :class="['msg', m.sender_id === userId ? 'msg-me' : 'msg-other']">
        <div class="msg-author">{{ m.sender_name }}</div>
        <div class="msg-bubble">{{ m.content }}</div>
        <div class="msg-time">{{ formatTime(m.created_at) }}</div>
      </div>
      <div v-if="!messages.length" class="chat-empty">暂无消息</div>
    </div>
    <div class="chat-input">
      <n-input v-model:value="text" placeholder="输入消息..." @keyup.enter="send" />
      <n-button type="primary" size="small" @click="send" :disabled="!text.trim()">发送</n-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  userId: { type: String, default: '' },
})

const emit = defineEmits(['send'])
const text = ref('')
const msgList = ref(null)

function send() {
  if (!text.value.trim()) return
  emit('send', text.value.trim())
  text.value = ''
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

watch(() => props.messages.length, () => {
  nextTick(() => {
    if (msgList.value) msgList.value.scrollTop = msgList.value.scrollHeight
  })
}, { flush: 'post' })
</script>

<style scoped>
.chat-box { display: flex; flex-direction: column; height: 360px; border: 1px solid #eee; border-radius: 12px; overflow: hidden; }
.chat-messages { flex: 1; overflow-y: auto; padding: 12px; background: #fafafa; }
.chat-empty { text-align: center; color: #ccc; padding-top: 80px; font-size: 14px; }
.msg { margin-bottom: 12px; max-width: 80%; }
.msg-me { margin-left: auto; text-align: right; }
.msg-other { margin-right: auto; }
.msg-author { font-size: 12px; color: #999; margin-bottom: 2px; }
.msg-bubble { display: inline-block; padding: 8px 14px; border-radius: 18px; font-size: 14px; line-height: 1.5; word-break: break-word; }
.msg-me .msg-bubble { background: #4f46e5; color: #fff; border-bottom-right-radius: 4px; }
.msg-other .msg-bubble { background: #fff; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.06); }
.msg-time { font-size: 11px; color: #bbb; margin-top: 2px; }
.chat-input { display: flex; gap: 8px; padding: 10px; background: #fff; border-top: 1px solid #eee; }
.chat-input :first-child { flex: 1; }
</style>
