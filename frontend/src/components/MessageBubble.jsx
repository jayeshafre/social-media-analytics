/**
 * MessageBubble.jsx
 *
 * Renders a single chat message — user, assistant, or error.
 *
 * Assistant bubble now includes:
 * - Markdown-rendered answer
 * - TermsGlossary (expandable) when terms_explained is present
 * - MetaBadges (intent/platform/confidence chips)
 */

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import MetaBadges from './MetaBadges'

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// ── Terms Glossary ────────────────────────────────────────────
// Expandable pill list of marketing terms detected in the response.
// Collapsed by default so it doesn't dominate the UI.
function TermsGlossary({ terms }) {
  const [expanded, setExpanded]       = useState(false)
  const [openTerm, setOpenTerm]       = useState(null)
  const [glossaryHovered, setGlossaryHovered] = useState(false)

  if (!terms || terms.length === 0) return null

  return (
    <div style={{
      marginTop:  '12px',
      borderTop:  '1px solid rgba(255,255,255,0.06)',
      paddingTop: '10px',
    }}>
      {/* ── Toggle header ─────────────────────────── */}
      <button
        onClick={() => setExpanded(p => !p)}
        onMouseEnter={() => setGlossaryHovered(true)}
        onMouseLeave={() => setGlossaryHovered(false)}
        style={{
          background:   'none',
          border:       'none',
          cursor:       'pointer',
          padding:      0,
          display:      'flex',
          alignItems:   'center',
          gap:          '7px',
          marginBottom: expanded ? '10px' : 0,
          width:        '100%',
        }}
      >
        {/* Book icon */}
        <span style={{
          fontSize:       '11px',
          background:     'rgba(250,204,21,0.1)',
          border:         '1px solid rgba(250,204,21,0.2)',
          borderRadius:   '5px',
          padding:        '2px 6px',
          color:          '#fbbf24',
          fontFamily:     'DM Mono, monospace',
          letterSpacing:  '0.04em',
          transition:     'all 0.15s ease',
          ...(glossaryHovered ? {
            background: 'rgba(250,204,21,0.18)',
            borderColor: 'rgba(250,204,21,0.4)',
          } : {}),
        }}>
          ◉ glossary
        </span>

        <span style={{
          color:      '#334155',
          fontFamily: 'DM Mono, monospace',
          fontSize:   '10px',
        }}>
          {terms.length} term{terms.length !== 1 ? 's' : ''} explained
        </span>

        {/* Chevron */}
        <span style={{
          marginLeft:  'auto',
          color:       '#1e3a5f',
          fontSize:    '10px',
          transition:  'transform 0.2s ease',
          transform:   expanded ? 'rotate(180deg)' : 'rotate(0deg)',
          display:     'inline-block',
        }}>
          ▾
        </span>
      </button>

      {/* ── Term pills + expanded definition ─────── */}
      {expanded && (
        <div style={{ animation: 'fadeInUp 0.2s ease-out' }}>
          {/* Pill row */}
          <div style={{
            display:  'flex',
            flexWrap: 'wrap',
            gap:      '6px',
            marginBottom: '10px',
          }}>
            {terms.map((t, i) => {
              const isOpen = openTerm === i
              return (
                <button
                  key={i}
                  onClick={() => setOpenTerm(isOpen ? null : i)}
                  style={{
                    padding:      '4px 10px',
                    borderRadius: '999px',
                    border:       isOpen
                      ? '1px solid rgba(250,204,21,0.45)'
                      : '1px solid rgba(255,255,255,0.1)',
                    background:   isOpen
                      ? 'rgba(250,204,21,0.12)'
                      : 'rgba(255,255,255,0.04)',
                    color:        isOpen ? '#fde68a' : '#64748b',
                    fontFamily:   'DM Mono, monospace',
                    fontSize:     '11px',
                    cursor:       'pointer',
                    transition:   'all 0.15s ease',
                    lineHeight:   1.4,
                  }}
                  onMouseEnter={e => {
                    if (!isOpen) {
                      e.currentTarget.style.borderColor = 'rgba(250,204,21,0.25)'
                      e.currentTarget.style.color       = '#94a3b8'
                    }
                  }}
                  onMouseLeave={e => {
                    if (!isOpen) {
                      e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'
                      e.currentTarget.style.color       = '#64748b'
                    }
                  }}
                >
                  {t.term}
                </button>
              )
            })}
          </div>

          {/* Expanded definition card */}
          {openTerm !== null && terms[openTerm] && (
            <div style={{
              background:   'rgba(250,204,21,0.05)',
              border:       '1px solid rgba(250,204,21,0.15)',
              borderRadius: '10px',
              padding:      '12px 14px',
              animation:    'fadeInUp 0.18s ease-out',
            }}>
              <div style={{
                display:      'flex',
                alignItems:   'center',
                gap:          '8px',
                marginBottom: '6px',
              }}>
                <span style={{
                  color:      '#fbbf24',
                  fontFamily: 'Syne, sans-serif',
                  fontWeight: 700,
                  fontSize:   '13px',
                }}>
                  {terms[openTerm].term}
                </span>
                <span style={{
                  width:        '1px',
                  height:       '12px',
                  background:   'rgba(250,204,21,0.2)',
                  display:      'inline-block',
                }} />
                <span style={{
                  color:      '#78350f',
                  fontFamily: 'DM Mono, monospace',
                  fontSize:   '9px',
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                }}>
                  marketing term
                </span>
              </div>
              <p style={{
                margin:     0,
                color:      '#a16207',
                fontFamily: 'Syne, sans-serif',
                fontSize:   '13px',
                lineHeight: 1.65,
              }}>
                {terms[openTerm].explanation}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ── User bubble ───────────────────────────────────────────────
function UserBubble({ message }) {
  return (
    <div style={{
      display:        'flex',
      justifyContent: 'flex-end',
      marginBottom:   '16px',
      animation:      'slideInRight 0.2s ease-out',
    }}>
      <div style={{
        maxWidth:     '72%',
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
      gap:          '12px',
      marginBottom: '24px',
      animation:    'slideInLeft 0.25s ease-out',
    }}>
      {/* Avatar */}
      <div style={{
        width:          '36px',
        height:         '36px',
        minWidth:       '36px',
        borderRadius:   '50%',
        background:     'linear-gradient(135deg, #0ea5e9, #7c3aed)',
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'center',
        fontSize:       '13px',
        fontWeight:     700,
        color:          '#fff',
        fontFamily:     'Syne, sans-serif',
        boxShadow:      '0 0 14px rgba(14,165,233,0.3)',
      }}>
        AI
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          background:     'rgba(255,255,255,0.04)',
          border:         '1px solid rgba(255,255,255,0.07)',
          borderRadius:   '4px 16px 16px 16px',
          padding:        '16px 18px',
          backdropFilter: 'blur(4px)',
        }}>
          {/* Answer */}
          <div className="ai-markdown">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>

          <span style={{
            display:    'block',
            marginTop:  '10px',
            fontSize:   '10px',
            color:      '#1e3a5f',
            fontFamily: 'DM Mono, monospace',
          }}>
            {formatTime(message.ts)}
          </span>

          {/* Terms glossary — shown when backend returns terms_explained */}
          <TermsGlossary terms={message.terms} />

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
      background:   'rgba(239,68,68,0.07)',
      border:       '1px solid rgba(239,68,68,0.2)',
      borderRadius: '10px',
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