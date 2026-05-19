/**
 * Sidebar.jsx
 *
 * Route-aware sidebar. Two distinct modes:
 *
 * CHAT MODE  (isDashboard = false)
 * ┌─────────────────┐
 * │  Brand          │
 * ├─────────────────┤
 * │  New Chat btn   │
 * ├─────────────────┤
 * │  RECENT CHATS   │
 * │  history list   │  ← scrollable, flex:1
 * ├─────────────────┤
 * │  View Dashboard │  ← navigates to /dashboard/executive
 * ├─────────────────┤
 * │  ● CONNECTED    │
 * └─────────────────┘
 *
 * DASHBOARD MODE  (isDashboard = true)
 * ┌─────────────────┐
 * │  Brand          │
 * ├─────────────────┤
 * │  DASHBOARD NAV  │
 * │  • Executive    │  ← each item navigates to /dashboard/:tab
 * │  • Campaigns    │
 * │  • Platforms    │
 * │  • Audience     │
 * │  • Alerts       │
 * ├─────────────────┤  flex:1 spacer
 * │  Return to Chat │  ← navigates to /chat
 * ├─────────────────┤
 * │  ● CONNECTED    │
 * └─────────────────┘
 */

import { useState } from 'react'

// ── Helpers ───────────────────────────────────────────────────

function timeAgo(ts) {
  const diff = Date.now() - ts
  const mins = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
}

// Dashboard tab definitions — single source of truth here
// Sidebar reads this; DashboardView uses its own TAB_CONFIG for labels/subtitles
const DASHBOARD_TABS = [
  { id: 'executive', icon: '▦', label: 'Executive', desc: 'KPIs & revenue overview' },
  { id: 'campaign', icon: '◈', label: 'Campaigns', desc: 'CTR, CPC & conversions' },
  { id: 'platform', icon: '⬡', label: 'Platforms', desc: 'Cross-platform benchmarks' },
  { id: 'audience', icon: '◉', label: 'Audience', desc: 'Age, device & sentiment' },
  { id: 'alerts', icon: '⚡', label: 'Alerts', desc: 'AI-generated warnings' },
]

// ── Sub-components ────────────────────────────────────────────

/** Shared brand block — identical in both modes */
function Brand() {
  return (
    <div style={{
      padding: '22px 20px 16px',
      borderBottom: '1px solid rgba(255,255,255,0.055)',
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: '34px',
          height: '34px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '16px',
          flexShrink: 0,
          boxShadow: '0 0 18px rgba(14,165,233,0.3)',
        }}>◈</div>
        <div>
          <div style={{
            color: '#f1f5f9',
            fontFamily: 'Syne, sans-serif',
            fontWeight: 700,
            fontSize: '14px',
            lineHeight: 1.2,
          }}>AI Analyst</div>
          <div style={{
            color: '#2a4a6a',
            fontFamily: 'DM Mono, monospace',
            fontSize: '9px',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
          }}>Marketing Intelligence</div>
        </div>
      </div>
    </div>
  )
}

/** Shared footer with connection status */
function Footer() {
  return (
    <div style={{ padding: '10px 18px 14px', flexShrink: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <div style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: '#22c55e',
          boxShadow: '0 0 6px rgba(34,197,94,0.5)',
          animation: 'subtlePulse 2s ease-in-out infinite',
        }} />
        <span style={{
          color: '#0f2744',
          fontFamily: 'DM Mono, monospace',
          fontSize: '9px',
          letterSpacing: '0.08em',
        }}>
          CONNECTED TO BACKEND
        </span>
      </div>
    </div>
  )
}

// ── Chat Mode Sidebar ─────────────────────────────────────────

function ChatSidebar({
  history,
  activeSessionId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onViewDashboard,
}) {
  const [hoveredId, setHoveredId] = useState(null)
  const [deleteHoverId, setDeleteHoverId] = useState(null)
  const [dashHovered, setDashHovered] = useState(false)

  return (
    <>
      {/* New Chat button */}
      <div style={{ padding: '14px 14px 10px', flexShrink: 0 }}>
        <button
          onClick={onNewChat}
          style={{
            width: '100%',
            padding: '10px 14px',
            background: 'linear-gradient(135deg, rgba(14,165,233,0.15) 0%, rgba(124,58,237,0.15) 100%)',
            border: '1px solid rgba(14,165,233,0.25)',
            borderRadius: '10px',
            color: '#7dd3fc',
            fontFamily: 'Syne, sans-serif',
            fontWeight: 600,
            fontSize: '13px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            justifyContent: 'center',
            transition: 'all 0.18s ease',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(14,165,233,0.25) 0%, rgba(124,58,237,0.25) 100%)'
            e.currentTarget.style.borderColor = 'rgba(14,165,233,0.5)'
            e.currentTarget.style.color = '#bae6fd'
            e.currentTarget.style.boxShadow = '0 0 20px rgba(14,165,233,0.15)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = 'linear-gradient(135deg, rgba(14,165,233,0.15) 0%, rgba(124,58,237,0.15) 100%)'
            e.currentTarget.style.borderColor = 'rgba(14,165,233,0.25)'
            e.currentTarget.style.color = '#7dd3fc'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          <span style={{ fontSize: '16px', lineHeight: 1 }}>✦</span>
          New Conversation
        </button>
      </div>

      {/* History label */}
      {history.length > 0 && (
        <div style={{
          padding: '8px 18px 6px',
          color: '#1e3a5f',
          fontSize: '9px',
          fontFamily: 'DM Mono, monospace',
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          flexShrink: 0,
        }}>
          Recent Chats
        </div>
      )}

      {/* History list — flex:1 scrollable */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '4px 10px 12px',
        scrollbarWidth: 'thin',
        scrollbarColor: '#0f2744 transparent',
      }}>
        {history.length === 0 && (
          <div style={{
            padding: '40px 16px',
            textAlign: 'center',
            color: '#0f2744',
            fontSize: '12px',
            fontFamily: 'DM Mono, monospace',
            lineHeight: 1.7,
          }}>
            No conversations yet.<br />Start one above.
          </div>
        )}

        {history.map(entry => {
          const isActive = entry.id === activeSessionId
          const isHovered = hoveredId === entry.id

          return (
            <div
              key={entry.id}
              onClick={() => onSelectChat(entry)}
              onMouseEnter={() => setHoveredId(entry.id)}
              onMouseLeave={() => setHoveredId(null)}
              style={{
                position: 'relative',
                padding: '10px 12px',
                borderRadius: '10px',
                cursor: 'pointer',
                marginBottom: '2px',
                background: isActive
                  ? 'linear-gradient(135deg, rgba(14,165,233,0.12) 0%, rgba(124,58,237,0.08) 100%)'
                  : isHovered ? 'rgba(255,255,255,0.04)' : 'transparent',
                border: isActive
                  ? '1px solid rgba(14,165,233,0.2)'
                  : '1px solid transparent',
                transition: 'all 0.15s ease',
              }}
            >
              {isActive && (
                <div style={{
                  position: 'absolute',
                  left: 0,
                  top: '20%',
                  bottom: '20%',
                  width: '2px',
                  borderRadius: '999px',
                  background: 'linear-gradient(180deg, #0ea5e9, #7c3aed)',
                }} />
              )}

              <div style={{
                color: isActive ? '#bae6fd' : '#64748b',
                fontFamily: 'Syne, sans-serif',
                fontSize: '12.5px',
                fontWeight: isActive ? 600 : 400,
                lineHeight: 1.4,
                paddingRight: '22px',
                overflow: 'hidden',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                transition: 'color 0.15s ease',
              }}>
                {entry.title}
              </div>
              <div style={{
                color: '#0f2744',
                fontFamily: 'DM Mono, monospace',
                fontSize: '9px',
                marginTop: '4px',
                letterSpacing: '0.04em',
              }}>
                {timeAgo(entry.ts)}
              </div>

              {(isHovered || isActive) && (
                <button
                  onClick={e => { e.stopPropagation(); onDeleteChat(entry.id) }}
                  onMouseEnter={() => setDeleteHoverId(entry.id)}
                  onMouseLeave={() => setDeleteHoverId(null)}
                  title="Delete conversation"
                  style={{
                    position: 'absolute',
                    top: '50%',
                    right: '8px',
                    transform: 'translateY(-50%)',
                    width: '20px',
                    height: '20px',
                    borderRadius: '5px',
                    background: deleteHoverId === entry.id
                      ? 'rgba(239,68,68,0.15)'
                      : 'rgba(255,255,255,0.05)',
                    border: deleteHoverId === entry.id
                      ? '1px solid rgba(239,68,68,0.3)'
                      : '1px solid rgba(255,255,255,0.08)',
                    color: deleteHoverId === entry.id ? '#f87171' : '#334155',
                    fontSize: '12px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.15s ease',
                    lineHeight: 1,
                  }}
                >×</button>
              )}
            </div>
          )
        })}
      </div>

      {/* View Dashboard button */}
      <div style={{ padding: '10px 14px', borderTop: '1px solid rgba(255,255,255,0.055)', flexShrink: 0 }}>
        <button
          onClick={onViewDashboard}
          onMouseEnter={() => setDashHovered(true)}
          onMouseLeave={() => setDashHovered(false)}
          style={{
            width: '100%',
            padding: '10px 14px',
            background: dashHovered ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.03)',
            border: dashHovered
              ? '1px solid rgba(255,255,255,0.12)'
              : '1px solid rgba(255,255,255,0.07)',
            borderRadius: '10px',
            color: dashHovered ? '#94a3b8' : '#475569',
            fontFamily: 'Syne, sans-serif',
            fontWeight: 600,
            fontSize: '12.5px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            justifyContent: 'center',
            transition: 'all 0.18s ease',
          }}
        >
          <span style={{ fontSize: '15px', lineHeight: 1 }}>▦</span>
          View Dashboard
        </button>
      </div>
    </>
  )
}

// ── Dashboard Mode Sidebar ────────────────────────────────────

function DashboardSidebar({ activeDashboardTab, onTabSelect, onGoToChat }) {
  const [hoveredTab, setHoveredTab] = useState(null)
  const [returnHovered, setReturnHovered] = useState(false)

  return (
    <>
      {/* Section label */}
      <div style={{
        padding: '14px 18px 8px',
        color: '#1e3a5f',
        fontSize: '9px',
        fontFamily: 'DM Mono, monospace',
        letterSpacing: '0.12em',
        textTransform: 'uppercase',
        flexShrink: 0,
      }}>
        Dashboard
      </div>

      {/* Tab nav list */}
      <div style={{
        flex: 1,
        padding: '4px 10px 12px',
        overflowY: 'auto',
        scrollbarWidth: 'thin',
        scrollbarColor: '#0f2744 transparent',
      }}>
        {DASHBOARD_TABS.map(tab => {
          const isActive = activeDashboardTab === tab.id
          const isHovered = hoveredTab === tab.id && !isActive

          return (
            <div
              key={tab.id}
              onClick={() => onTabSelect(tab.id)}
              onMouseEnter={() => setHoveredTab(tab.id)}
              onMouseLeave={() => setHoveredTab(null)}
              style={{
                position: 'relative',
                padding: '11px 14px',
                borderRadius: '10px',
                cursor: 'pointer',
                marginBottom: '3px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                background: isActive
                  ? 'linear-gradient(135deg, rgba(14,165,233,0.13) 0%, rgba(124,58,237,0.09) 100%)'
                  : isHovered
                    ? 'rgba(255,255,255,0.04)'
                    : 'transparent',
                border: isActive
                  ? '1px solid rgba(14,165,233,0.22)'
                  : '1px solid transparent',
                transition: 'all 0.15s ease',
              }}
            >
              {/* Active left bar */}
              {isActive && (
                <div style={{
                  position: 'absolute',
                  left: 0,
                  top: '20%',
                  bottom: '20%',
                  width: '2px',
                  borderRadius: '999px',
                  background: 'linear-gradient(180deg, #0ea5e9, #7c3aed)',
                }} />
              )}

              {/* Icon */}
              <div style={{
                width: '28px',
                height: '28px',
                borderRadius: '7px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '13px',
                flexShrink: 0,
                background: isActive
                  ? 'rgba(14,165,233,0.15)'
                  : isHovered
                    ? 'rgba(255,255,255,0.06)'
                    : 'rgba(255,255,255,0.03)',
                border: isActive
                  ? '1px solid rgba(14,165,233,0.2)'
                  : '1px solid rgba(255,255,255,0.06)',
                transition: 'all 0.15s ease',
              }}>
                {tab.icon}
              </div>

              {/* Label + desc */}
              <div style={{ minWidth: 0 }}>
                <div style={{
                  color: isActive ? '#bae6fd' : isHovered ? '#94a3b8' : '#64748b',
                  fontFamily: 'Syne, sans-serif',
                  fontWeight: isActive ? 700 : 500,
                  fontSize: '12.5px',
                  lineHeight: 1.3,
                  transition: 'color 0.15s ease',
                }}>
                  {tab.label}
                </div>
                <div style={{
                  color: isActive ? '#1e4a6a' : '#0f2744',
                  fontFamily: 'DM Mono, monospace',
                  fontSize: '9px',
                  letterSpacing: '0.03em',
                  marginTop: '2px',
                  transition: 'color 0.15s ease',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}>
                  {tab.desc}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Return to Chat button */}
      <div style={{ padding: '10px 14px', borderTop: '1px solid rgba(255,255,255,0.055)', flexShrink: 0 }}>
        <button
          onClick={onGoToChat}
          onMouseEnter={() => setReturnHovered(true)}
          onMouseLeave={() => setReturnHovered(false)}
          style={{
            width: '100%',
            padding: '10px 14px',
            background: returnHovered
              ? 'linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(14,165,233,0.15) 100%)'
              : 'linear-gradient(135deg, rgba(124,58,237,0.08) 0%, rgba(14,165,233,0.08) 100%)',
            border: returnHovered
              ? '1px solid rgba(124,58,237,0.35)'
              : '1px solid rgba(124,58,237,0.18)',
            borderRadius: '10px',
            color: returnHovered ? '#c4b5fd' : '#7c5cbf',
            fontFamily: 'Syne, sans-serif',
            fontWeight: 600,
            fontSize: '12.5px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            justifyContent: 'center',
            transition: 'all 0.18s ease',
            boxShadow: returnHovered ? '0 0 16px rgba(124,58,237,0.12)' : 'none',
          }}
        >
          <span style={{ fontSize: '14px', lineHeight: 1 }}>◧</span>
          Return to Chat
        </button>
      </div>
    </>
  )
}

// ── Main Sidebar ──────────────────────────────────────────────

export default function Sidebar({
  // Chat mode props
  history,
  activeSessionId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  // Route state
  isDashboard,
  activeDashboardTab,
  onDashboardTabSelect,
  onGoToChat,
}) {
  // "View Dashboard" navigates to executive tab by default
  const handleViewDashboard = () => onDashboardTabSelect('executive')

  return (
    <aside style={{
      width: '260px',
      minWidth: '260px',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: '#07090f',
      borderRight: '1px solid rgba(255,255,255,0.055)',
      overflow: 'hidden',
    }}>

      {/* Brand — always shown */}
      <Brand />

      {/* Mode-specific content */}
      {isDashboard
        ? (
          <DashboardSidebar
            activeDashboardTab={activeDashboardTab}
            onTabSelect={onDashboardTabSelect}
            onGoToChat={onGoToChat}
          />
        )
        : (
          <ChatSidebar
            history={history}
            activeSessionId={activeSessionId}
            onNewChat={onNewChat}
            onSelectChat={onSelectChat}
            onDeleteChat={onDeleteChat}
            onViewDashboard={handleViewDashboard}
          />
        )
      }

      {/* Footer — always shown */}
      <Footer />
    </aside>
  )
}