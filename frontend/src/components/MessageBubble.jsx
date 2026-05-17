/**
 * MessageBubble.jsx
 *
 * Renders a single message — user, assistant, or error.
 * AI responses are rendered as Markdown (supports bold, lists, code).
 */

import ReactMarkdown from 'react-markdown'
import MetaBadges from './MetaBadges'

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// ── User bubble ───────────────────────────────────────────────
function UserBubble({ message }) {
  return (
    <div style={{
      display:       'flex',
      justifyContent:'flex-end',
      marginBottom:  '16px',
      animation:     'slideInRight 0.2s ease-out',
    }}>
      <div style={{
        maxWidth:     '78%',
        background:   'linear-gradient(135deg, #1a3a5c 0%, #0f2744 100%)',
        border:       '1px solid #1e4a7a',
        borderRadius: '16px 16px 4px 16px',
        padding:      '12px 16px',
      }}>
        <p style={{
          margin:     0,
          color:      '#e2e8f0',
          fontSize:   '14px',
          lineHeight: '1.6',
          fontFamily: 'Syne, sans-serif',
          fontWeight: 400,
        }}>
          {message.content}
        </p>
        <span style={{
          display:    'block',
          marginTop:  '6px',
          fontSize:   '10px',
          color:      '#4a6fa5',
          fontFamily: 'DM Mono, monospace',
          textAlign:  'right',
        }}>
          {formatTime(message.ts)}
        </span>
      </div>
    </div>
  )
}

// ── Assistant bubble ──────────────────────────────────────────
function AssistantBubble({ message }) {
  return (
    <div style={{
      display:      'flex',
      gap:          '10px',
      marginBottom: '20px',
      animation:    'slideInLeft 0.25s ease-out',
    }}>
      {/* Avatar */}
      <div style={{
        width:          '32px',
        height:         '32px',
        minWidth:       '32px',
        borderRadius:   '50%',
        background:     'linear-gradient(135deg, #0ea5e9, #8b5cf6)',
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'center',
        fontSize:       '14px',
        fontWeight:     700,
        color:          '#fff',
        fontFamily:     'Syne, sans-serif',
        boxShadow:      '0 0 12px rgba(14,165,233,0.3)',
      }}>
        AI
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          background:   'rgba(255,255,255,0.04)',
          border:       '1px solid rgba(255,255,255,0.08)',
          borderRadius: '4px 16px 16px 16px',
          padding:      '14px 16px',
          backdropFilter: 'blur(4px)',
        }}>
          {/* Markdown-rendered response */}
          <div className="ai-markdown">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          <span style={{
            display:    'block',
            marginTop:  '8px',
            fontSize:   '10px',
            color:      '#334155',
            fontFamily: 'DM Mono, monospace',
          }}>
            {formatTime(message.ts)}
          </span>

          {/* Intelligence badges */}
          <MetaBadges meta={message.meta} />
        </div>
      </div>
    </div>
  )
}

// ── Error bubble ──────────────────────────────────────────────
function ErrorBubble({ message }) {
  return (
    <div style={{
      background:   'rgba(239,68,68,0.08)',
      border:       '1px solid rgba(239,68,68,0.25)',
      borderRadius: '8px',
      padding:      '10px 14px',
      marginBottom: '16px',
      color:        '#f87171',
      fontSize:     '13px',
      fontFamily:   'DM Mono, monospace',
    }}>
      ⚠ {message.content}
    </div>
  )
}

// ── Main export ───────────────────────────────────────────────
export default function MessageBubble({ message }) {
  if (message.role === 'user')      return <UserBubble message={message} />
  if (message.role === 'assistant') return <AssistantBubble message={message} />
  if (message.role === 'error')     return <ErrorBubble message={message} />
  return null
}