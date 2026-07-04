<template>
  <div class="home-page">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6" v-for="item in cards" :key="item.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" :style="{ background: item.color }">
            <el-icon :size="28" color="#fff"><component :is="item.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ item.value }}</div>
            <div class="stat-label">{{ item.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header><span>近 7 天问答量趋势</span></template>
          <div ref="lineChartRef" style="height: 350px"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header><span>文档类型分布</span></template>
          <div ref="pieChartRef" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/**
 * 管理后台首页 - 数据统计图表
 */
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getStatsOverview, getStatsTrend } from '../../api/stats'

const cards = ref([
  { label: '用户总数', value: 0, icon: 'User', color: '#409EFF' },
  { label: '文档总数', value: 0, icon: 'Document', color: '#67C23A' },
  { label: '会话总数', value: 0, icon: 'ChatDotRound', color: '#E6A23C' },
  { label: '今日问答', value: 0, icon: 'ChatLineRound', color: '#F56C6C' },
])

const lineChartRef = ref(null)
const pieChartRef = ref(null)
let lineChart = null
let pieChart = null

/** 加载统计数据 */
async function loadData() {
  const overview = await getStatsOverview()
  cards.value[0].value = overview.user_count
  cards.value[1].value = overview.document_count
  cards.value[2].value = overview.session_count
  cards.value[3].value = overview.today_message_count

  const trend = await getStatsTrend()
  renderLineChart(trend.daily_messages)
  renderPieChart(trend.doc_types)
}

/** 渲染折线图 */
function renderLineChart(data) {
  if (!lineChartRef.value) return
  lineChart = echarts.init(lineChartRef.value)
  lineChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map((d) => d.date) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{
      name: '问答量',
      type: 'line',
      smooth: true,
      data: data.map((d) => d.count),
      areaStyle: { color: 'rgba(64,158,255,0.15)' },
      itemStyle: { color: '#409EFF' },
    }],
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
  })
}

/** 渲染饼图 */
function renderPieChart(data) {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      data: data.length ? data.map((d) => ({ name: d.type, value: d.count })) : [{ name: '暂无数据', value: 0 }],
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.2)' } },
    }],
  })
}

onMounted(loadData)
onUnmounted(() => {
  lineChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.stat-cards {
  margin-bottom: 0;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
</style>
