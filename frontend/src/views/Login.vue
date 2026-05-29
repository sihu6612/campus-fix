<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo">
        <n-icon size="48" color="#4f46e5"><BuildOutline /></n-icon>
        <h1>校修通</h1>
        <p>CampusFix</p>
      </div>

      <n-tabs v-model:value="tab" type="segment" animated>
        <n-tab-pane name="login" tab="登录" />
        <n-tab-pane name="register" tab="注册" />
      </n-tabs>

      <n-form v-if="tab === 'login'" @submit.prevent="handleLogin">
        <n-form-item><n-input v-model:value="email" placeholder="邮箱" clearable size="large" /></n-form-item>
        <n-form-item><n-input v-model:value="password" type="password" placeholder="密码" show-password-on="click" size="large" @keyup.enter="handleLogin" /></n-form-item>
        <n-button type="primary" block size="large" :loading="loading" @click="handleLogin">{{ loading ? '登录中...' : '登录' }}</n-button>
      </n-form>

      <n-form v-else @submit.prevent="handleRegister">
        <n-form-item><n-input v-model:value="email" placeholder="邮箱" clearable size="large" /></n-form-item>
        <n-form-item><n-input v-model:value="displayName" placeholder="你的名字" clearable size="large" /></n-form-item>
        <n-form-item>
          <n-select v-model:value="regRole" placeholder="选择角色" :options="roleOptions" size="large" />
        </n-form-item>
        <n-form-item v-if="regRole === 'counselor'">
          <n-input v-model:value="className" placeholder="班级（如：软件工程2101）" clearable size="large" />
        </n-form-item>
        <n-form-item><n-input v-model:value="password" type="password" placeholder="密码（至少6位）" show-password-on="click" size="large" /></n-form-item>
        <n-button type="primary" block size="large" :loading="loading" @click="handleRegister">{{ loading ? '注册中...' : '注册' }}</n-button>
      </n-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { BuildOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const message = useMessage()
const auth = useAuthStore()

const tab = ref('login')
const email = ref('')
const password = ref('')
const displayName = ref('')
const regRole = ref('student')
const className = ref('')
const loading = ref(false)

const roleOptions = [
  { label: '学生', value: 'student' },
  { label: '维修师傅', value: 'worker' },
  { label: '物业管理员', value: 'admin' },
  { label: '辅导员', value: 'counselor' },
]

async function handleLogin() {
  loading.value = true
  try {
    const user = await auth.login(email.value, password.value)
    if (user.role === 'admin') router.push('/admin')
    else if (user.role === 'worker') router.push('/worker')
    else if (user.role === 'counselor') router.push('/counselor')
    else router.push('/student')
  } catch (e) {
    message.error(e.message || '登录失败')
  }
  loading.value = false
}

async function handleRegister() {
  if (password.value.length < 6) {
    message.warning('密码至少6位')
    return
  }
  if (regRole.value === 'counselor' && !className.value.trim()) {
    message.warning('辅导员请填写班级')
    return
  }
  loading.value = true
  try {
    await auth.register(email.value, password.value, displayName.value, regRole.value, className.value)
    message.success('注册成功！请检查邮箱确认（或在 Supabase 关闭邮箱验证）')
  } catch (e) {
    message.error(e.message || '注册失败')
  }
  loading.value = false
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 16px;
}
.login-card {
  width: 100%; max-width: 400px; background: #fff; border-radius: 16px; padding: 32px 24px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}
.logo { text-align: center; margin-bottom: 24px; }
.logo h1 { font-size: 24px; margin: 8px 0 4px; color: #333; }
.logo p { font-size: 13px; color: #999; }

@media (min-width: 768px) {
  .login-card { padding: 40px 36px; box-shadow: 0 24px 80px rgba(0,0,0,0.2); }
}
</style>
