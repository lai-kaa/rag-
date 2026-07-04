/**
 * 文档管理 API
 */
import request from './request'

export function getDocuments() {
  return request.get('/documents')
}

export function uploadDocument(formData) {
  return request.post('/documents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function deleteDocument(id) {
  return request.delete(`/documents/${id}`)
}
