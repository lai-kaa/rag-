<template>
  <div class="chat-page">
    <!-- 左侧会话列表 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>知识库问答</h2>
        <el-button type="primary" :icon="Plus" circle size="small" @click="handleNewSession" />
      </div>

      <div class="session-list">
        <div
          v-for="s in sessions"
          :key="s.id"
          :class="['session-item', { active: s.id === currentSessionId }]"
          @click="selectSession(s.id)"
        >
          <el-icon><ChatDotRound /></el-icon>
          <span class="session-title">{{ s.title }}</span>
          <el-icon class="delete-btn" @click.stop="handleDeleteSession(s.id)"><Delete /></el-icon>
        </div>
      </div>

      <div class="sidebar-footer">
        <span>{{ userStore.user?.username }}</span>
        <el-button v-if="userStore.isAdmin()" text type="primary" @click="$router.push('/admin/home')">
          管理后台
        </el-button>
        <el-button text type="danger" @click="handleLogout">退出</el-button>
      </div>
    </aside>

    <!-- 右侧对话区 -->
    <main class="chat-main">
      <div v-if="!currentSessionId" class="empty-chat">
        <el-icon :size="64" color="#dcdfe6"><ChatLineRound /></el-icon>
        <p>选择或创建一个对话开始提问</p>
      </div>

      <template v-else>
        <div class="messages" ref="messagesRef">
          <div v-for="msg in messages" :key="msg.id" :class="['message', msg.role]">
            <div class="avatar">
              <el-icon v-if="msg.role === 'user'"><User /></el-icon>
              <el-icon v-else><Monitor /></el-icon>
            </div>
            <div class="bubble">
              <div class="content">{{ msg.content }}</div>
              <div v-if="msg.sources?.length" class="sources">
                <el-collapse accordion class="source-collapse">
                  <el-collapse-item :name="`sources-${msg.id}`">
                    <template #title>
                      <span class="sources-title">
                        <el-icon><Document /></el-icon>
                        引用来源（{{ msg.sources.length }}）
                      </span>
                    </template>
                    <el-collapse accordion class="source-list">
                      <el-collapse-item
                        v-for="(src, i) in msg.sources"
                        :key="i"
                        :name="`${msg.id}-${i}`"
                      >
                        <template #title>
                          <div class="source-header">
                            <span class="source-index">{{ i + 1 }}</span>
                            <span class="source-name">{{ src.title }}</span>
                            <el-tag
                              v-if="src.score != null"
                              size="small"
                              :type="scoreTagType(src.score)"
                              class="score-tag"
                            >
                              相似度 {{ formatScore(src.score) }}
                            </el-tag>
                          </div>
                        </template>
                        <div class="source-body">
                          <p v-if="src.source" class="source-file">文件：{{ src.source }}</p>
                          <pre class="source-content">{{ src.content }}</pre>
                        </div>
                      </el-collapse-item>
                    </el-collapse>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
          </div>
          <div v-if="asking" class="message assistant">
            <div class="avatar"><el-icon><Monitor /></el-icon></div>
            <div class="bubble"><div class="content typing">正在思考中...</div></div>
          </div>
        </div>

        <div class="input-area">
          <el-input
            v-model="question"
            type="textarea"
            :rows="2"
            placeholder="输入你的问题，按 Enter 发送..."
            @keydown.enter.exact.prevent="handleAsk"
          />
          <el-button type="primary" :loading="asking" @click="handleAsk">发送</el-button>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
/**
 * 问答主界面组件
 */
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Document } from '@element-plus/icons-vue'
import { useUserStore } from '../../stores/user'
import { getSessions, createSession, deleteSession, getMessages, askQuestion } from '../../api/chat'

const router = useRouter()
const userStore = useUserStore()

const sessions = ref([])
const currentSessionId = ref(null)
const messages = ref([])
const question = ref('')
const asking = ref(false)
const messagesRef = ref(null)

/** 加载会话列表 */
async function loadSessions() {
  sessions.value = await getSessions()
}

/** 创建新会话 */
async function handleNewSession() {
  const session = await createSession({ title: '新对话' })
  sessions.value.unshift(session)
  selectSession(session.id)
}

/** 选择会话 */
async function selectSession(id) {
  currentSessionId.value = id
  messages.value = await getMessages(id)
  scrollToBottom()
}

/** 删除会话 */
async function handleDeleteSession(id) {
  await ElMessageBox.confirm('确定删除该会话？', '提示', { type: 'warning' })
  await deleteSession(id)
  sessions.value = sessions.value.filter((s) => s.id !== id)
  if (currentSessionId.value === id) {
    currentSessionId.value = null
    messages.value = []
  }
  ElMessage.success('已删除')
}

/** 发送问题 */
async function handleAsk() {
  if (!question.value.trim() || asking.value) return
  const q = question.value.trim()
  question.value = ''
  asking.value = true

  messages.value.push({ id: Date.now(), role: 'user', content: q })

  try {
    const res = await askQuestion({ session_id: currentSessionId.value, question: q })
    messages.value.push({
      id: res.message_id,
      role: 'assistant',
      content: res.answer,
      sources: res.sources,
    })
    await loadSessions()
  } finally {
    asking.value = false
    scrollToBottom()
  }
}

/** 格式化相似度得分（0~1 → 百分比） */
function formatScore(score) {
  if (score == null) return '--'
  return `${Math.round(Number(score) * 100)}%`
}

/** 根据相似度选择标签颜色 */
function scoreTagType(score) {
  const pct = Number(score) * 100
  if (pct >= 70) return 'success'
  if (pct >= 50) return 'warning'
  return 'info'
}

/** 滚动到底部 */
function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

/** 退出登录 */
function handleLogout() {
  userStore.logout()
  router.push('/login')
}

onMounted(loadSessions)
</script>

<style scoped>
.chat-page {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e4e7ed;
}

.sidebar-header h2 {
  font-size: 16px;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.session-item:hover,
.session-item.active {
  background: #ecf5ff;
}

.session-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.delete-btn {
  opacity: 0;
  color: #f56c6c;
}

.session-item:hover .delete-btn {
  opacity: 1;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #909399;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.empty-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  gap: 16px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #409EFF;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .avatar {
  background: #67c23a;
}

.bubble {
  max-width: 70%;
}

.content {
  padding: 12px 16px;
  border-radius: 12px;
  background: #fff;
  line-height: 1.6;
  font-size: 14px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.message.user .content {
  background: #409EFF;
  color: #fff;
}

.typing {
  color: #909399;
}

.sources {
  margin-top: 10px;
}

.source-collapse {
  border: none;
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

.sources-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.source-list {
  border: none;
}

.source-header {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding-right: 8px;
}

.source-index {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.source-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  color: #303133;
}

.score-tag {
  flex-shrink: 0;
}

.source-body {
  padding: 4px 0 8px 28px;
}

.source-file {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.source-content {
  margin: 0;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #ebeef5;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.7;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-word;
}

.input-area {
  padding: 16px 24px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}
</style>
