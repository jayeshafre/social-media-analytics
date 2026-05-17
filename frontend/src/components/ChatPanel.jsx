/**
 * ChatPanel.jsx — Full-screen main area version.
 *
 * Now renders as the persistent right-side main column,
 * not a slide-in overlay. Sits next to the Sidebar.
 *
 * Contains:
 * - Top header bar (session info, turn count, model badge)
 * - Scrollable messages area
 * - Fixed input bar at bottom
 */

import ChatMessages from './ChatMessages'
import ChatInput from './ChatInput'

export default function ChatPanel({
  messages,
  sessionId,
  isLoading,
  lastMeta,
  bottomRef,
  sendMessage,
  clearConversation,
}) {
  return (
    <div style={{
      flex:          1,
      height:        '100vh',
      display:       'flex',
      flexDirection: 'column',
      background:    'linear-gradient(160deg, #080d18 0%, #050a12 50%, #080d18 100%)',
      overflow:      'hidden',
      position:      'relative',
    }}>

      {/* ── Subtle grid background texture ──────────── */}
      <div style={{
        position:   'absolute',
        inset:      0,
        backgroundImage: `
          linear-gradient(rgba(14,165,233,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(14,165,233,0.03) 1px, transparent 1px)
        `,
        backgroundSize: '48px 48px',
        pointerEvents: 'none',
        zIndex: 0,
      }} />

      {/* ── Header bar ─────────────────────────────── */}
      <div style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        padding:        '14px 28px',
        borderBottom:   '1px solid rgba(255,255,255,0.055)',
        flexShrink:     0,
        zIndex:         1,
        backdropFilter: 'blur(8px)',
        background:     'rgba(5,10,18,0.6)',
      }}>
        {/* Left — session info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {sessionId ? (
            <>
              <div style={{
                width:        '8px',
                height:       '8px',
                borderRadius: '50%',
                background:   '#22c55e',
                boxShadow:    '0 0 8px rgba(34,197,94,0.6)',
              }} />
              <span style={{
                color:      '#1e3a5f',
                fontFamily: 'DM Mono, monospace',
                fontSize:   '11px',
                letterSpacing: '0.04em',
              }}>
                session · {sessionId.slice(0, 8)}…
              </span>
            </>
          ) : (
            <span style={{
              color:      '#0f2744',
              fontFamily: 'DM Mono, monospace',
              fontSize:   '11px',
            }}>
              no active session
            </span>
          )}
        </div>

        {/* Right — meta pills */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {lastMeta && (
            <>
              <span style={{
                background:   'rgba(255,255,255,0.04)',
                border:       '1px solid rgba(255,255,255,0.07)',
                borderRadius: '999px',
                padding:      '3px 10px',
                color:        '#334155',
                fontFamily:   'DM Mono, monospace',
                fontSize:     '10px',
              }}>
                {lastMeta.turnCount} turns
              </span>
              <span style={{
                background:   'rgba(14,165,233,0.08)',
                border:       '1px solid rgba(14,165,233,0.15)',
                borderRadius: '999px',
                padding:      '3px 10px',
                color:        '#38bdf8',
                fontFamily:   'DM Mono, monospace',
                fontSize:     '10px',
              }}>
                {lastMeta.model?.split('-').slice(0, 3).join('-')}
              </span>
            </>
          )}

          {messages.length > 0 && (
            <button
              onClick={clearConversation}
              style={{
                background:   'rgba(255,255,255,0.04)',
                border:       '1px solid rgba(255,255,255,0.08)',
                borderRadius: '8px',
                padding:      '5px 12px',
                color:        '#334155',
                fontFamily:   'DM Mono, monospace',
                fontSize:     '10px',
                cursor:       'pointer',
                transition:   'all 0.15s ease',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.color = '#f87171'
                e.currentTarget.style.borderColor = 'rgba(248,113,113,0.25)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.color = '#334155'
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'
              }}
            >
              clear chat
            </button>
          )}
        </div>
      </div>

      {/* ── Messages ───────────────────────────────── */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', zIndex: 1 }}>
        <ChatMessages
          messages={messages}
          isLoading={isLoading}
          bottomRef={bottomRef}
          onSuggest={sendMessage}
        />
      </div>

      {/* ── Input ──────────────────────────────────── */}
      <div style={{ zIndex: 1 }}>
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  )
}