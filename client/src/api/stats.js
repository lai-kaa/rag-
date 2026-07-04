/**
 * 统计数据 API
 */
import request from './request'

export function getStatsOverview() {
  return request.get('/stats/overview')
}

export function getStatsTrend() {
  return request.get('/stats/trend')
}
