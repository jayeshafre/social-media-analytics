/**
 * App.jsx
 *
 * Root application shell.
 *
 * Route map:
 *   /chat                   → ChatPanel  (default)
 *   /dashboard/:tab         → DashboardView
 *   *                       → redirect to /chat
 *
 * Sidebar is always rendered. It reads the current route via
 * useLocation() to decide which mode to show — no props needed
 * for that decision. Chat-related callbacks still flow as props
 * so Sidebar can trigger navigation + session changes together.
 */

import { useCallback } from 'react'
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { useChat }        from './hooks/useChat'
import { useChatHistory } from './hooks/useChatHistory'
import Sidebar            from './components/Sidebar'
import ChatPanel          from './components/ChatPanel'
import DashboardView      from './components/dashboard/DashboardView'

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()

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

  // ── Sidebar callbacks ────────────────────────────────────────

  const handleNewChat = useCallback(() => {
    clearConversation()
    navigate('/chat')
  }, [clearConversation, navigate])

  const handleSelectChat = useCallback((entry) => {
    loadSession(entry)
    navigate('/chat')
  }, [loadSession, navigate])

  const handleDeleteChat = useCallback((id) => {
    removeEntry(id)
    if (id === sessionId) clearConversation()
  }, [removeEntry, sessionId, clearConversation])

  // Navigate to a specific dashboard tab from the sidebar nav
  const handleDashboardTabSelect = useCallback((tabId) => {
    navigate(`/dashboard/${tabId}`)
  }, [navigate])

  // Go back to chat from dashboard sidebar button
  const handleGoToChat = useCallback(() => {
    navigate('/chat')
  }, [navigate])

  // Derive active dashboard tab from the URL for the sidebar
  const isDashboard   = location.pathname.startsWith('/dashboard')
  const activeTabInUrl = isDashboard
    ? location.pathname.split('/dashboard/')[1] || 'executive'
    : null

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', overflow: 'hidden' }}>

      {/* Sidebar is always visible — it adapts based on current route */}
      <Sidebar
        // Chat props
        history={history}
        activeSessionId={sessionId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        // Route state
        isDashboard={isDashboard}
        activeDashboardTab={activeTabInUrl}
        onDashboardTabSelect={handleDashboardTabSelect}
        onGoToChat={handleGoToChat}
      />

      {/* Main content area — driven entirely by the URL */}
      <Routes>
        <Route path="/chat" element={
          <ChatPanel
            messages={messages}
            sessionId={sessionId}
            isLoading={isLoading}
            lastMeta={lastMeta}
            bottomRef={bottomRef}
            sendMessage={sendMessage}
            clearConversation={clearConversation}
          />
        } />

        {/*
          /dashboard/:tab — the :tab param tells DashboardView
          which tab to activate. DashboardView reads it via
          useParams() so no prop drilling needed.
        */}
        <Route path="/dashboard/:tab" element={<DashboardView />} />

        {/* Redirect /dashboard (no tab) → executive */}
        <Route path="/dashboard" element={<Navigate to="/dashboard/executive" replace />} />

        {/* Catch-all → chat */}
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </div>
  )
}