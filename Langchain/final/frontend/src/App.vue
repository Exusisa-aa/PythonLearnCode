<script setup>
import { ref, nextTick, onMounted, reactive } from 'vue'
import {
  listSessions,
  createSession,
  deleteSession,
  getHistory,
  streamMessage,
} from './api'

const sessions = ref([])
const currentId = ref(null)
const messages = ref([])
const input = ref('')
const streaming = ref(false)
const error = ref('')

const chatBody = ref(null)

async function loadSessions() {
  sessions.value = await listSessions()
}

async function selectSession(id) {
  currentId.value = id
  error.value = ''
  messages.value = await getHistory(id)
  scrollToBottom()
}

async function handleNew() {
  try {
    const session = await createSession()
    await loadSessions()
    await selectSession(session.id)
  } catch (e) {
    error.value = e.message
  }
}

async function handleDelete(id) {
  try {
    await deleteSession(id)
    if (currentId.value === id) {
      currentId.value = null
      messages.value = []
    }
    await loadSessions()
  } catch (e) {
    error.value = e.message
  }
}

async function handleSend() {
  const content = input.value.trim()
  if (!content || streaming.value || !currentId.value) return

  input.value = ''
  error.value = ''
  messages.value.push({ role: 'user', content })

  streaming.value = true
  const assistant = reactive({ role: 'assistant', content: '' })
  messages.value.push(assistant)

  try {
    await streamMessage(currentId.value, content, {
      onToken: (token) => {
        assistant.content += token
        scrollToBottom()
      },
      onDone: () => {
        scrollToBottom()
      },
    })
  } catch (e) {
    error.value = e.message
    assistant.content = assistant.content || '（生成失败）'
  } finally {
    streaming.value = false
    scrollToBottom()
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatBody.value) {
      chatBody.value.scrollTop = chatBody.value.scrollHeight
    }
  })
}

onMounted(loadSessions)
</script>

<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">🤖 Agent Chat</div>
      <button class="new-btn" @click="handleNew">＋ 新建会话</button>

      <div class="session-list">
        <div
          v-for="s in sessions"
          :key="s.id"
          class="session-item"
          :class="{ active: s.id === currentId }"
          @click="selectSession(s.id)"
        >
          <span class="session-title">{{ s.id.slice(0, 8) }}</span>
          <button class="del-btn" title="删除" @click.stop="handleDelete(s.id)">✕</button>
        </div>
        <div v-if="sessions.length === 0" class="empty">暂无会话</div>
      </div>
    </aside>

    <main class="chat">
      <div v-if="error" class="error-bar">{{ error }}</div>

      <div class="chat-body" ref="chatBody">
        <div v-if="messages.length === 0" class="welcome">
          <div class="welcome-title">开始新的对话</div>
          <div class="welcome-sub">选择左侧会话，或点击「新建会话」</div>
        </div>

        <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role">
          <div class="bubble">
            <span v-if="m.role === 'assistant' && m.content === '' && streaming" class="typing">
              <span></span><span></span><span></span>
            </span>
            <template v-else>{{ m.content }}</template>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <textarea
          v-model="input"
          :disabled="streaming || !currentId"
          placeholder="输入消息…（Enter 发送，Shift+Enter 换行）"
          @keydown.enter.exact.prevent="handleSend"
        ></textarea>
        <button class="send-btn" :disabled="streaming || !currentId || !input.trim()" @click="handleSend">
          发送
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100%;
}

.sidebar {
  width: 260px;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  display: flex;
  flex-direction: column;
  padding: 16px;
  flex-shrink: 0;
}

.brand {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.new-btn {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 16px;
}

.new-btn:hover {
  opacity: 0.9;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.session-item:hover {
  background: var(--sidebar-hover);
}

.session-item.active {
  background: var(--sidebar-hover);
  color: #fff;
}

.del-btn {
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 14px;
  opacity: 0;
}

.session-item:hover .del-btn {
  opacity: 1;
}

.del-btn:hover {
  color: var(--danger);
}

.empty {
  font-size: 13px;
  color: var(--muted);
  text-align: center;
  margin-top: 20px;
}

.chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.error-bar {
  background: #fdecec;
  color: var(--danger);
  padding: 10px 16px;
  font-size: 14px;
  border-bottom: 1px solid #f5c6c6;
}

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.welcome {
  margin: auto;
  text-align: center;
  color: var(--muted);
}

.welcome-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 8px;
}

.welcome-sub {
  font-size: 14px;
}

.msg {
  display: flex;
}

.msg.user {
  justify-content: flex-end;
}

.msg.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.msg.user .bubble {
  background: var(--bubble-user);
  color: var(--bubble-user-text);
  border-bottom-right-radius: 4px;
}

.msg.assistant .bubble {
  background: var(--bubble-assistant);
  border: 1px solid #e8eaf0;
  border-bottom-left-radius: 4px;
}

.typing {
  display: inline-flex;
  gap: 4px;
  padding: 4px 0;
}

.typing span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--muted);
  animation: blink 1.2s infinite;
}

.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0%, 60%, 100% { opacity: 0.3; }
  30% { opacity: 1; }
}

.chat-input {
  display: flex;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid #e8eaf0;
  background: #fff;
}

.chat-input textarea {
  flex: 1;
  resize: none;
  border: 1px solid #dfe3ec;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 15px;
  font-family: inherit;
  min-height: 48px;
  max-height: 160px;
  outline: none;
}

.chat-input textarea:focus {
  border-color: var(--accent);
}

.send-btn {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0 22px;
  font-size: 15px;
  cursor: pointer;
}

.send-btn:disabled {
  background: #c3c9d8;
  cursor: not-allowed;
}
</style>
