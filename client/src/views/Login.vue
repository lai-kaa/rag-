<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <el-icon :size="40" color="#409EFF"><Reading /></el-icon>
        <h1>企业知识库问答系统</h1>
        <p>基于 LangChain RAG 的智能问答平台</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleLogin" style="width: 100%">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-tip">
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 登录页面组件
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

/** 处理登录 */
async function handleLogin() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    if (userStore.isAdmin()) {
      router.push('/admin/home')
    } else {
      router.push('/chat')
    }
  } catch (e) {
    // 错误提示已在 axios 拦截器中处理
    console.error('登录失败:', e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  font-size: 22px;
  margin: 12px 0 8px;
  color: #303133;
}

.login-header p {
  font-size: 13px;
  color: #909399;
}

.login-tip {
  margin-top: 16px;
  text-align: center;
  font-size: 12px;
  color: #c0c4cc;
  line-height: 1.8;
}
</style>
