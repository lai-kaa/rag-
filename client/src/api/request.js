/**
 * Axios 请求封装
 *
 * 开发环境：baseURL 默认 /api，由 Vite 代理到本地后端
 * 生产环境：在构建时设置 VITE_API_BASE_URL 指向真实后端，例如
 *   https://your-api.example.com/api
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

const request = axios.create({
  baseURL,
  timeout: 120000,
})

// 请求拦截：自动附加 JWT Token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：统一错误处理
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    const isLoginRequest = error.config?.url?.includes('/auth/login')

    // 网络错误或后端未启动
    if (!error.response) {
      ElMessage.error('无法连接后端服务，请确认 API 地址正确且后端已启动')
      return Promise.reject(error)
    }

    // 生产环境未配置后端时，静态站点会对 /api 返回 405
    if (status === 405 && baseURL === '/api' && import.meta.env.PROD) {
      ElMessage.error('未配置后端 API 地址，请在构建时设置 VITE_API_BASE_URL')
      return Promise.reject(error)
    }

    const msg = detail || '请求失败'

    // 登录接口的 401 仅提示错误，不跳转（避免刷新页面导致提示消失）
    if (status === 401 && isLoginRequest) {
      ElMessage.error(typeof msg === 'string' ? msg : '用户名或密码错误')
      return Promise.reject(error)
    }

    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    ElMessage.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
    return Promise.reject(error)
  }
)

export default request
