import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../views/Login.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: Login },
  { path: '/student', name: 'student-home', component: () => import('../views/student/StudentHome.vue') },
  { path: '/student/create', name: 'student-create', component: () => import('../views/student/CreateOrder.vue') },
  { path: '/student/order/:id', name: 'student-order', component: () => import('../views/student/OrderDetail.vue') },
  { path: '/student/confirm/:id', name: 'student-confirm', component: () => import('../views/student/ConfirmFix.vue') },
  { path: '/worker', name: 'worker-home', component: () => import('../views/worker/WorkerHome.vue') },
  { path: '/worker/order/:id', name: 'worker-order', component: () => import('../views/worker/WorkOrder.vue') },
  { path: '/admin', name: 'admin-dashboard', component: () => import('../views/admin/AdminDashboard.vue') },
  { path: '/admin/order/:id', name: 'admin-order', component: () => import('../views/student/OrderDetail.vue') },
  { path: '/counselor', name: 'counselor-home', component: () => import('../views/counselor/CounselorHome.vue') },
  { path: '/counselor/order/:id', name: 'counselor-order', component: () => import('../views/counselor/CounselorOrder.vue') },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from) => {
  const session = localStorage.getItem('cf_session')
  if (!session && to.path !== '/login') {
    return '/login'
  }
  if (session && to.path === '/login') {
    const user = JSON.parse(localStorage.getItem('cf_user') || '{}')
    if (user.role === 'admin') return '/admin'
    if (user.role === 'worker') return '/worker'
    if (user.role === 'counselor') return '/counselor'
    return '/student'
  }
})

export default router
