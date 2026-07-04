/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getMe } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  /** 是否已登录 */
  const isLoggedIn = () => !!token.value

  /** 是否为管理员 */
  const isAdmin = () => user.value?.role === 'admin'

  /** 用户登录 */
  async function login(username, password) {
    const res = await loginApi({ username, password })
    token.value = res.access_token
    user.value = { id: res.user_id, username: res.username, role: res.role }
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(user.value))
    return res
  }

  /** 退出登录 */
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  /** 刷新用户信息 */
  async function fetchUser() {
    if (!token.value) return
    const res = await getMe()
    user.value = res
    localStorage.setItem('user', JSON.stringify(res))
  }

  return { token, user, isLoggedIn, isAdmin, login, logout, fetchUser }
})
