import { useState, useCallback } from 'react'
import { useChat } from './hooks/useChat'
import { useChatHistory } from './hooks/useChatHistory'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'
import DashboardView from './components/dashboard/DashboardView'

export default function App() {
  const [showDashboard, setShowDashboard] = useState(false)

  const { history, upsertEntry, removeEntry } = useChatHistory()

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
    setShowDashboard(false)
  }, [clearConversation])

  const handleSelectChat = useCallback((entry) => {
    loadSession(entry)
    setShowDashboard(false)
  }, [loadSession])

  const handleDeleteChat = useCallback((id) => {
    removeEntry(id)
    if (id === sessionId) clearConversation()
  }, [removeEntry, sessionId, clearConversation])

  const handleToggleDashboard = useCallback(() => {
    setShowDashboard(prev => !prev)
  }, [])

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <Sidebar
        history={history}
        activeSessionId={sessionId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        showDashboard={showDashboard}
        onToggleDashboard={handleToggleDashboard}
      />

      {showDashboard
        ? <DashboardView />
        : (
          <ChatPanel
            messages={messages}
            sessionId={sessionId}
            isLoading={isLoading}
            lastMeta={lastMeta}
            bottomRef={bottomRef}
            sendMessage={sendMessage}
            clearConversation={clearConversation}
          />
        )
      }
    </div>
  )
}