import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../views/Login.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'login', component: Login, meta: { layout: false } },
  { path: '/student', name: 'student-home', component: () => import('../views/student/StudentHome.vue'), meta: { layout: true, title: '我的报修' } },
  { path: '/student/create', name: 'student-create', component: () => import('../views/student/CreateOrder.vue'), meta: { layout: true, title: '新建报修', showBack: true, backTo: '/student' } },
  { path: '/student/order/:id', name: 'student-order', component: () => import('../views/student/OrderDetail.vue'), meta: { layout: true, title: '工单详情', showBack: true, backTo: '/student' } },
  { path: '/student/confirm/:id', name: 'student-confirm', component: () => import('../views/student/ConfirmFix.vue'), meta: { layout: true, title: '确认完工', showBack: true } },
  { path: '/worker', name: 'worker-home', component: () => import('../views/worker/WorkerHome.vue'), meta: { layout: true, title: '师傅工作台' } },
  { path: '/worker/order/:id', name: 'worker-order', component: () => import('../views/worker/WorkOrder.vue'), meta: { layout: true, title: '工单操作', showBack: true, backTo: '/worker' } },
  { path: '/worker/route', name: 'worker-route', component: () => import('../views/worker/RouteMap.vue'), meta: { layout: false, title: '维修路线' } },
  { path: '/admin', name: 'admin-dashboard', component: () => import('../views/admin/AdminDashboard.vue'), meta: { layout: true, title: '物业管理' } },
  { path: '/admin/order/:id', name: 'admin-order', component: () => import('../views/student/OrderDetail.vue'), meta: { layout: true, title: '工单详情', showBack: true, backTo: '/admin' } },
  { path: '/counselor', name: 'counselor-home', component: () => import('../views/counselor/CounselorHome.vue'), meta: { layout: true, title: '班级管理' } },
  { path: '/counselor/order/:id', name: 'counselor-order', component: () => import('../views/counselor/CounselorOrder.vue'), meta: { layout: true, title: '工单详情', showBack: true, backTo: '/counselor' } },
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
