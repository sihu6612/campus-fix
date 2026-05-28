<template>
  <!-- FAB 按钮 -->
  <button v-show="!agentPanelOpen" class="agent-fab" @click="openPanel">
    <n-icon size="24"><ChatbubblesOutline /></n-icon>
  </button>

  <!-- 遮罩 -->
  <div v-show="agentPanelOpen" class="agent-overlay" @click="closePanel" />

  <!-- 聊天面板 -->
  <div v-show="agentPanelOpen" class="agent-panel">
    <div class="panel-header">
      <span class="panel-title">小修 · AI 助手</span>
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
    <div v-if="messages.length <= 1 && quickList.length" class="quick-actions">
      <n-button v-for="(q, i) in quickList" :key="i" size="tiny" secondary @click="sendQuick(q)">
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
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ChatbubblesOutline, CloseOutline, SendOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth.js'
import { api } from '../composables/useSupabase.js'
import { agentPanelOpen } from '../composables/useAgent.js'

const route = useRoute()
const auth = useAuthStore()

const text = ref('')
const loading = ref(false)
const msgList = ref(null)

const messages = ref([
  { role: 'assistant', content: '嗨～我是小修，校修通的 AI 助手！有什么可以帮你的吗？(｡･ω･｡)ﾉ', time: fmtNow() },
])

const allQuestions = {
  student: ['如何查看维修进度？', '怎么取消工单？', '报修后多久有人处理？'],
  worker: ['如何接单？', '完工后怎么操作？', '怎么看工单详情？'],
  admin: ['如何分配师傅？', '怎么看维修统计？', '工单状态有哪些？'],
}

const quickList = computed(() => allQuestions[auth.role] || allQuestions.student)

function fmtNow() {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function openPanel() {
  agentPanelOpen.value = true
}

function closePanel() {
  agentPanelOpen.value = false
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
    // 构建历史消息（不含当前消息和时间字段）
    const history = messages.value.slice(0, -1).map(m => ({
      role: m.role,
      content: m.content,
    }))
    const data = await api('/api/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: content,
        role: auth.role || 'student',
        page: route.name || route.path,
        order_id: route.params.id || null,
        history,
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

watch(agentPanelOpen, (v) => { if (v) scrollBottom() })
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
.agent-fab:hover { transform: scale(1.08); }
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
</style>
