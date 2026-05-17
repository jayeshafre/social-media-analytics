/**
 * App.jsx — Full-screen layout.
 *
 * Layout:
 * ┌──────────────┬────────────────────────────────┐
 * │   Sidebar    │         ChatPanel               │
 * │  (260px)     │         (flex: 1)               │
 * │ - Brand      │ - Header bar                    │
 * │ - New Chat   │ - Scrollable messages           │
 * │ - History    │ - Input bar                     │
 * └──────────────┴────────────────────────────────┘
 */

import { useCallback } from 'react'
import { useChat } from './hooks/useChat'
import { useChatHistory } from './hooks/useChatHistory'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'

export default function App() {
  const { history, upsertEntry, removeEntry } = useChatHistory()

  // Wire up the exchange callback so every AI reply is recorded in sidebar
  const handleExchange = useCallback((sessionId, userMsg, aiMsg) => {
    upsertEntry(sessionId, userMsg, aiMsg)
  }, [upsertEntry])

  const {
    messages,
    sessionId,
    isLoading,
    lastMeta,
    bottomRef,
    sendMessage,
    clearConversation,
    loadSession,
  } = useChat({ onExchange: handleExchange })

  const handleNewChat = useCallback(() => {
    clearConversation()
  }, [clearConversation])

  const handleSelectChat = useCallback((entry) => {
    loadSession(entry)
  }, [loadSession])

  const handleDeleteChat = useCallback((id) => {
    removeEntry(id)
    // If the deleted chat is the active one, start fresh
    if (id === sessionId) clearConversation()
  }, [removeEntry, sessionId, clearConversation])

  return (
    <div style={{
      display:  'flex',
      width:    '100vw',
      height:   '100vh',
      overflow: 'hidden',
    }}>
      <Sidebar
        history={history}
        activeSessionId={sessionId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
      />
      <ChatPanel
        messages={messages}
        sessionId={sessionId}
        isLoading={isLoading}
        lastMeta={lastMeta}
        bottomRef={bottomRef}
        sendMessage={sendMessage}
        clearConversation={clearConversation}
      />
    </div>
  )
}