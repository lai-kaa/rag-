/**
 * 路由配置与守卫
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/chat/Chat.vue'),
  },
  {
    path: '/admin',
    component: () => import('../views/admin/Layout.vue'),
    meta: { admin: true },
    children: [
      { path: '', redirect: '/admin/home' },
      { path: 'home', name: 'AdminHome', component: () => import('../views/admin/Home.vue') },
      { path: 'documents', name: 'AdminDocuments', component: () => import('../views/admin/Documents.vue') },
      { path: 'users', name: 'AdminUsers', component: () => import('../views/admin/Users.vue') },
    ],
  },
  { path: '/', redirect: '/chat' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：登录校验与角色权限
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()

  if (to.meta.public) {
    if (to.path === '/login' && userStore.isLoggedIn()) {
      next(userStore.isAdmin() ? '/admin/home' : '/chat')
      return
    }
    next()
    return
  }

  if (!userStore.isLoggedIn()) {
    next('/login')
    return
  }

  if (to.meta.admin && !userStore.isAdmin()) {
    next('/chat')
    return
  }

  next()
})

export default router
