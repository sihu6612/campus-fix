<template>
  <div class="agent-chat">
    <!-- FAB 按钮 -->
    <Transition name="fab-zoom">
      <button v-if="!panelOpen" class="agent-fab" @click="openPanel">
        <n-icon size="24"><ChatbubblesOutline /></n-icon>
      </button>
    </Transition>

    <!-- 遮罩 -->
    <Transition name="fade">
      <div v-if="panelOpen" class="agent-overlay" @click="closePanel" />
    </Transition>

    <!-- 聊天面板 -->
    <Transition name="slide-up">
      <div v-if="panelOpen" class="agent-panel">
        <div class="panel-header">
          <span class="panel-title">智能助手</span>
          <n-button text size="small" @click="closePanel">
            <n-icon size="20"><CloseOutline /></n-icon>
          </n-button>
        </div>

        <div class="panel-messages" ref="msgList">
          <div v-for="(m, i) in messages" :key="i" :class="['msg', m.role === 'user' ? 'msg-me' : 'msg-other']">
            <div class="msg-bubble">{{ m.content }}</div>
            <div class="msg-time">{{ m.time }}</div>
          </div>
          <div v-if="loading" class="msg msg-other">
            <div class="msg-bubble typing"><span /><span /><span /></div>
          </div>
        </div>

        <!-- 快捷提问 -->
        <div v-if="messages.length <= 1" class="quick-actions">
          <n-button v-for="q in quickQuestions" :key="q" size="tiny" secondary @click="sendQuick(q)">
            {{ q }}
          </n-button>
        </div>

        <div class="panel-input">
          <n-input v-model:value="text" placeholder="输入问题..." size="small" @keyup.enter="send" />
          <n-button type="primary" size="small" :disabled="!text.trim() || loading" @click="send">
            <template #icon><n-icon size="16"><SendOutline /></n-icon></template>
          </n-button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ChatbubblesOutline, CloseOutline, SendOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth.js'
import { api } from '../composables/useSupabase.js'

const route = useRoute()
const auth = useAuthStore()

const panelOpen = ref(false)
const text = ref('')
const loading = ref(false)
const msgList = ref(null)

const messages = ref([
  { role: 'assistant', content: '你好！我是校修通智能助手，有什么可以帮你的吗？(๑•̀ㅂ•́)و✧', time: fmtNow() },
])

const quickQuestions = {
  student: ['如何查看维修进度？', '怎么取消工单？', '报修后多久有人处理？'],
  worker: ['如何接单？', '完工后怎么操作？', '怎么看工单详情？'],
  admin: ['如何分配师傅？', '怎么看维修统计？', '工单状态有哪些？'],
}

function fmtNow() {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function openPanel() {
  panelOpen.value = true
}

function closePanel() {
  panelOpen.value = false
}

function sendQuick(q) {
  text.value = q
  send()
}

async function send() {
  if (!text.value.trim() || loading.value) return
  const content = text.value.trim()
  text.value = ''
  messages.value.push({ role: 'user', content, time: fmtNow() })
  loading.value = true
  scrollBottom()

  try {
    const data = await api('/api/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: content,
        role: auth.role || 'student',
        page: route.name || route.path,
        order_id: route.params.id || null,
      }),
    })
    messages.value.push({ role: 'assistant', content: data.reply, time: fmtNow() })
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，网络出现问题，请稍后再试。', time: fmtNow() })
  } finally {
    loading.value = false
    scrollBottom()
  }
}

function scrollBottom() {
  nextTick(() => {
    if (msgList.value) msgList.value.scrollTop = msgList.value.scrollHeight
  })
}

watch(panelOpen, (v) => { if (v) scrollBottom() })
</script>

<style scoped>
.agent-fab {
  position: fixed; bottom: 24px; right: 24px; z-index: 999;
  width: 52px; height: 52px; border-radius: 50%;
  background: #4f46e5; color: #fff; border: none;
  box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
}
.agent-fab:hover { transform: scale(1.08); box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5); }
.agent-fab:active { transform: scale(0.95); }

.agent-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.25);
}

.agent-panel {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 1001;
  height: 60vh; max-height: 520px;
  background: #fff; border-radius: 20px 20px 0 0;
  display: flex; flex-direction: column;
  box-shadow: 0 -4px 24px rgba(0,0,0,0.12);
}

.panel-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 18px; border-bottom: 1px solid #f0f0f0;
}
.panel-title { font-size: 16px; font-weight: 600; color: #333; }

.panel-messages {
  flex: 1; overflow-y: auto; padding: 12px 16px; background: #fafafa;
}

.msg { margin-bottom: 12px; max-width: 85%; }
.msg-me { margin-left: auto; }
.msg-other { margin-right: auto; }
.msg-bubble {
  display: inline-block; padding: 8px 14px; border-radius: 16px;
  font-size: 14px; line-height: 1.5; word-break: break-word;
}
.msg-me .msg-bubble { background: #4f46e5; color: #fff; border-bottom-right-radius: 4px; }
.msg-other .msg-bubble { background: #fff; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.06); }
.msg-time { font-size: 11px; color: #bbb; margin-top: 2px; }
.msg-me .msg-time { text-align: right; }

.typing { display: flex; gap: 4px; padding: 4px 0; }
.typing span {
  width: 7px; height: 7px; border-radius: 50%; background: #bbb;
  animation: typing 1.4s infinite ease-in-out;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

.quick-actions {
  display: flex; gap: 8px; padding: 8px 16px; flex-wrap: wrap;
  border-top: 1px solid #f0f0f0;
}

.panel-input {
  display: flex; gap: 8px; padding: 10px 16px;
  border-top: 1px solid #f0f0f0;
  padding-bottom: max(10px, env(safe-area-inset-bottom));
}
.panel-input > :first-child { flex: 1; }

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-up-enter-active, .slide-up-leave-active { transition: transform 0.3s ease; }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(100%); }

.fab-zoom-enter-active, .fab-zoom-leave-active { transition: transform 0.25s, opacity 0.25s; }
.fab-zoom-enter-from, .fab-zoom-leave-to { transform: scale(0); opacity: 0; }
</style>
