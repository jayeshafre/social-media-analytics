/**
 * App.jsx — Full-screen layout with Superset Dashboard.
 *
 * Dashboard view embeds Apache Superset via iframe.
 * Superset runs at http://localhost:8088
 *
 * HOW TO GET YOUR EMBED URL (after Superset is running):
 * 1. Open http://localhost:8088
 * 2. Login: admin / admin
 * 3. Build your dashboard
 * 4. Click the dashboard → ··· menu → "Embed Dashboard"
 * 5. Copy the UUID shown
 * 6. Paste it into SUPERSET_DASHBOARD_UUID below
 *
 * The embed URL format is:
 * http://localhost:8088/superset/dashboard/<UUID>/?standalone=3
 *
 * standalone=3 hides Superset navbar — shows only the dashboard.
 */

import { useState, useCallback } from 'react'
import { useChat } from './hooks/useChat'
import { useChatHistory } from './hooks/useChatHistory'
import Sidebar from './components/Sidebar'
import ChatPanel from './components/ChatPanel'

// ── Superset config ───────────────────────────────────────────
// After setting up Superset and creating a dashboard,
// paste your dashboard UUID here.
// Leave empty to show the setup instructions placeholder.
const SUPERSET_DASHBOARD_UUID = ''  // e.g. 'abc123-def456-...'

const SUPERSET_BASE = 'http://localhost:8088'

// standalone=3 → hides nav, tabs, filters bar — clean embed
const SUPERSET_EMBED_URL = SUPERSET_DASHBOARD_UUID
  ? `${SUPERSET_BASE}/superset/dashboard/${SUPERSET_DASHBOARD_UUID}/?standalone=3&expand_filters=0`
  : ''

// ── Dashboard view ────────────────────────────────────────────
function DashboardView() {
  if (!SUPERSET_EMBED_URL) {
    return (
      <div style={{
        flex:           1,
        height:         '100vh',
        display:        'flex',
        flexDirection:  'column',
        alignItems:     'center',
        justifyContent: 'center',
        background:     'linear-gradient(160deg, #080d18 0%, #050a12 50%, #080d18 100%)',
        gap:            '24px',
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
        <div style={{ fontSize: '52px', opacity: 0.12, zIndex: 1 }}>▦</div>

        {/* Title */}
        <div style={{ textAlign: 'center', zIndex: 1 }}>
          <p style={{
            color:      '#1e3a5f',
            fontFamily: 'Syne, sans-serif',
            fontWeight: 700,
            fontSize:   '18px',
            margin:     '0 0 8px',
          }}>
            Apache Superset Dashboard
          </p>
          <p style={{
            color:      '#0f2744',
            fontFamily: 'DM Mono, monospace',
            fontSize:   '11px',
            lineHeight: 1.8,
          }}>
            Follow the setup steps below to connect your dashboard.
          </p>
        </div>

        {/* Setup steps */}
        {[
          {
            step: '01',
            title: 'Start Superset',
            code: 'docker-compose up superset',
            note: 'Wait ~60 seconds for first-time init',
          },
          {
            step: '02',
            title: 'Open Superset & Login',
            code: 'http://localhost:8088',
            note: 'Username: admin  /  Password: admin',
          },
          {
            step: '03',
            title: 'Connect your PostgreSQL database',
            code: 'Settings → Database Connections → + Database',
            note: 'postgresql+psycopg2://postgres:PASSWORD@localhost:5433/social_media_analytics',
          },
          {
            step: '04',
            title: 'Create charts & a dashboard',
            code: 'Charts → + Chart → pick your table → build',
            note: 'Use campaigns, revenue, engagement_metrics tables',
          },
          {
            step: '05',
            title: 'Get the embed UUID',
            code: 'Dashboard → ··· menu → Embed Dashboard → copy UUID',
            note: 'Paste UUID into SUPERSET_DASHBOARD_UUID in src/App.jsx',
          },
        ].map(({ step, title, code, note }) => (
          <div key={step} style={{
            background:   'rgba(14,165,233,0.04)',
            border:       '1px solid rgba(14,165,233,0.1)',
            borderRadius: '12px',
            padding:      '14px 20px',
            zIndex:       1,
            width:        '100%',
            maxWidth:     '520px',
            margin:       '0 24px',
          }}>
            <div style={{ display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
              <span style={{
                color:         '#0ea5e9',
                fontFamily:    'DM Mono, monospace',
                fontSize:      '11px',
                fontWeight:    700,
                opacity:       0.6,
                flexShrink:    0,
                paddingTop:    '2px',
              }}>
                {step}
              </span>
              <div>
                <p style={{
                  color:      '#334155',
                  fontFamily: 'Syne, sans-serif',
                  fontWeight: 600,
                  fontSize:   '12px',
                  margin:     '0 0 4px',
                }}>
                  {title}
                </p>
                <code style={{
                  display:      'block',
                  color:        '#38bdf8',
                  fontFamily:   'DM Mono, monospace',
                  fontSize:     '11px',
                  background:   'rgba(14,165,233,0.08)',
                  border:       '1px solid rgba(14,165,233,0.15)',
                  borderRadius: '6px',
                  padding:      '4px 8px',
                  marginBottom: '4px',
                  wordBreak:    'break-all',
                }}>
                  {code}
                </code>
                <p style={{
                  color:      '#0f2744',
                  fontFamily: 'DM Mono, monospace',
                  fontSize:   '10px',
                  margin:     0,
                  lineHeight: 1.6,
                }}>
                  {note}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  // Real Superset embed — shown once UUID is configured
  return (
    <div style={{ flex: 1, height: '100vh', overflow: 'hidden' }}>
      <iframe
        title="Marketing Intelligence Dashboard"
        src={SUPERSET_EMBED_URL}
        style={{
          width:   '100%',
          height:  '100%',
          border:  'none',
          display: 'block',
        }}
        allowFullScreen
        // Required for Superset session cookie to work in iframe
        sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
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