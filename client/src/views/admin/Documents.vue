<template>
  <div class="documents-page">
    <!-- 上传区域 -->
    <el-card shadow="hover" class="upload-card">
      <template #header><span>上传知识库文档</span></template>
      <el-form inline @submit.prevent="handleUpload">
        <el-form-item label="文档标题">
          <el-input v-model="uploadTitle" placeholder="可选，默认使用文件名" style="width: 240px" />
        </el-form-item>
        <el-form-item>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".pdf,.txt,.docx"
            :on-change="handleFileChange"
          >
            <el-button type="primary">选择文件</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="success" :loading="uploading" @click="handleUpload">上传并向量化</el-button>
        </el-form-item>
      </el-form>
      <p class="tip">支持 PDF、TXT、DOCX 格式，上传后自动切分并向量化入库</p>
      <p class="tip sample-tip">样本文档目录：server/uploads/samples/（含加班晚下班配套制度，建议上传补齐知识库）</p>
    </el-card>

    <!-- 文档列表 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header><span>文档列表</span></template>
      <el-table :data="documents" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="180" />
        <el-table-column prop="file_name" label="文件名" min-width="160" />
        <el-table-column prop="file_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ row.file_type.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="chunk_count" label="切片数" width="80" />
        <el-table-column prop="created_at" label="上传时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" text size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 文档管理页面组件
 */
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDocuments, uploadDocument, deleteDocument } from '../../api/documents'

const documents = ref([])
const loading = ref(false)
const uploading = ref(false)
const uploadTitle = ref('')
const selectedFile = ref(null)
const uploadRef = ref(null)

/** 加载文档列表 */
async function loadDocuments() {
  loading.value = true
  try {
    documents.value = await getDocuments()
  } finally {
    loading.value = false
  }
}

/** 文件选择回调 */
function handleFileChange(file) {
  selectedFile.value = file.raw
}

/** 上传文档 */
async function handleUpload() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    if (uploadTitle.value) formData.append('title', uploadTitle.value)
    await uploadDocument(formData)
    ElMessage.success('上传并向量化成功')
    uploadTitle.value = ''
    selectedFile.value = null
    uploadRef.value?.clearFiles()
    await loadDocuments()
  } finally {
    uploading.value = false
  }
}

/** 删除文档 */
async function handleDelete(id) {
  await ElMessageBox.confirm('确定删除该文档？向量数据也会同步删除。', '提示', { type: 'warning' })
  await deleteDocument(id)
  ElMessage.success('已删除')
  await loadDocuments()
}

/** 格式化文件大小 */
function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

/** 格式化时间 */
function formatTime(t) {
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(loadDocuments)
</script>

<style scoped>
.tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.sample-tip {
  color: #e6a23c;
}
</style>
