const BASE = '/sessions'

async function request(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (res.status === 204) return null
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const data = await res.json()
      if (data.detail) detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  return res.json()
}

export const listSessions = () => request(BASE)
export const createSession = () => request(BASE, { method: 'POST' })
export const deleteSession = (id) => request(`${BASE}/${id}`, { method: 'DELETE' })
export const getHistory = (id) => request(`${BASE}/${id}/messages`)

// 流式消费：逐 token 回调，返回完整文本。
export async function streamMessage(id, content, { onToken, onDone }) {
  const res = await fetch(`${BASE}/${id}/messages/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const data = await res.json()
      if (data.detail) detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let full = ''
  let eventType = 'message'
  let dataLines = []

  const dispatch = () => {
    const data = dataLines.join('\n')
    dataLines = []
    if (eventType === 'token' && data) {
      full += data
      onToken && onToken(data)
    } else if (eventType === 'done') {
      onDone && onDone()
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    let idx
    while ((idx = buffer.indexOf('\n')) !== -1) {
      const line = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 1)
      const trimmed = line.endsWith('\r') ? line.slice(0, -1) : line

      if (trimmed === '') {
        // 空行 = 一个事件结束
        dispatch()
        eventType = 'message'
        continue
      }
      if (trimmed.startsWith(':')) continue // 注释/心跳行
      if (trimmed.startsWith('event:')) {
        eventType = trimmed.slice(6).trim()
      } else if (trimmed.startsWith('data:')) {
        dataLines.push(trimmed.slice(5).trimStart())
      }
    }
  }
  dispatch()
  return full
}
