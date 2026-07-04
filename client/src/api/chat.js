/**
 * 问答相关 API
 */
import request from './request'

export function getSessions() {
  return request.get('/chat/sessions')
}

export function createSession(data) {
  return request.post('/chat/sessions', data)
}

export function deleteSession(id) {
  return request.delete(`/chat/sessions/${id}`)
}

export function getMessages(sessionId) {
  return request.get(`/chat/sessions/${sessionId}/messages`)
}

export function askQuestion(data) {
  return request.post('/chat/ask', data)
}
