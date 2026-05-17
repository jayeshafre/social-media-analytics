/**
 * App.jsx — Full-screen layout with Dashboard toggle.
 *
 * Main area renders either:
 *   - ChatPanel   (default)
 *   - DashboardView (when showDashboard === true)
 *
 * The sidebar always stays visible.
 * The toggle button at the bottom of the sidebar switches views.
 *
 * ┌──────────────┬────────────────────────────────────┐
 * │   Sidebar    │  ChatPanel  OR  DashboardView       │
 * │  (260px)     │  (flex: 1)                          │
 * │              │                                     │
 * │  [New Chat]  │                                     │
 * │  history...  │                                     │
 * │              │                                     │
 * │  [Dashboard] │                                     │
 * │  ● connected │                                     │
 * └──────────────┴────────────────────────────────────┘
 */

import { useState, useCallback } from 'react'
import { useChat } from './hooks/useChat'
import { useChatHistory } from './hooks/useChatHistory'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'

// ── Dashboard view ────────────────────────────────────────────
// Replace POWERBI_EMBED_URL with your actual embed URL.
// Format: https://app.powerbi.com/reportEmbed?reportId=XXX&autoAuth=true
//
// To get this URL from Power BI:
//   File → Publish to web → Get embed link (iFrame option)
const POWERBI_EMBED_URL = ''  // ← paste your URL here

function DashboardView() {
  if (!POWERBI_EMBED_URL) {
    // Placeholder shown until the real URL is configured
    return (
      <div style={{
        flex:           1,
        height:         '100vh',
        display:        'flex',
        flexDirection:  'column',
        alignItems:     'center',
        justifyContent: 'center',
        background:     'linear-gradient(160deg, #080d18 0%, #050a12 50%, #080d18 100%)',
        gap:            '20px',
        position:       'relative',
        overflow:       'hidden',
      }}>
        {/* Grid texture */}
        <div style={{
          position:        'absolute',
          inset:           0,
          backgroundImage: `
            linear-gradient(rgba(14,165,233,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(14,165,233,0.03) 1px, transparent 1px)
          `,
          backgroundSize:  '48px 48px',
          pointerEvents:   'none',
        }} />

        {/* Icon */}
        <div style={{
          fontSize:   '56px',
          opacity:    0.15,
          zIndex:     1,
          lineHeight: 1,
        }}>▦</div>

        {/* Text */}
        <div style={{ textAlign: 'center', zIndex: 1 }}>
          <p style={{
            color:      '#1e3a5f',
            fontFamily: 'Syne, sans-serif',
            fontWeight: 600,
            fontSize:   '16px',
            margin:     '0 0 10px',
          }}>
            Power BI Dashboard
          </p>
          <p style={{
            color:      '#0f2744',
            fontFamily: 'DM Mono, monospace',
            fontSize:   '11px',
            lineHeight: 1.8,
          }}>
            Open <code style={{ color: '#1e3a5f' }}>src/App.jsx</code><br />
            and set <code style={{ color: '#1e3a5f' }}>POWERBI_EMBED_URL</code><br />
            to your Power BI embed link.
          </p>
        </div>

        {/* Step hint */}
        <div style={{
          background:   'rgba(14,165,233,0.06)',
          border:       '1px solid rgba(14,165,233,0.12)',
          borderRadius: '12px',
          padding:      '14px 20px',
          zIndex:       1,
          maxWidth:     '440px',
          width:        '100%',
          margin:       '0 24px',
        }}>
          <p style={{
            color:      '#1e3a5f',
            fontFamily: 'DM Mono, monospace',
            fontSize:   '11px',
            lineHeight: 1.8,
            margin:     0,
          }}>
            <span style={{ color: '#38bdf8' }}>How to get your embed URL:</span><br />
            1. Open your report in Power BI Service<br />
            2. File → Embed report → Website or portal<br />
            3. Copy the <strong style={{ color: '#7dd3fc' }}>src</strong> URL from the iframe code<br />
            4. Paste it into POWERBI_EMBED_URL in App.jsx
          </p>
        </div>
      </div>
    )
  }

  return (
    <div style={{ flex: 1, height: '100vh', overflow: 'hidden' }}>
      <iframe
        title="Marketing Intelligence Dashboard"
        src={POWERBI_EMBED_URL}
        style={{
          width:  '100%',
          height: '100%',
          border: 'none',
          display: 'block',
        }}
        allowFullScreen
      />
    </div>
  )
}

// ── App root ──────────────────────────────────────────────────
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
    setShowDashboard(false)   // always switch to chat on new conversation
  }, [clearConversation])

  const handleSelectChat = useCallback((entry) => {
    loadSession(entry)
    setShowDashboard(false)   // clicking a history item opens chat view
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

      {/* Main area — swaps between chat and dashboard */}
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