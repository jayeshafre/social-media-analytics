/**
 * ChatInput.jsx
 *
 * Input bar at the bottom of the chat panel.
 * - Enter to send, Shift+Enter for newline
 * - Disabled while loading
 * - Auto-grows up to 4 lines
 */

import { useState, useRef, useEffect } from 'react'

export default function ChatInput({ onSend, isLoading }) {
  const [value, setValue]   = useState('')
  const textareaRef         = useRef(null)

  // Auto-resize textarea height
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 100) + 'px'
  }, [value])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSend = () => {
    if (!value.trim() || isLoading) return
    onSend(value)
    setValue('')
    // Reset height
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  return (
    <div style={{
      padding:      '12px 16px 16px',
      borderTop:    '1px solid rgba(255,255,255,0.06)',
      background:   'rgba(0,0,0,0.2)',
    }}>
      <div style={{
        display:      'flex',
        gap:          '10px',
        alignItems:   'flex-end',
        background:   'rgba(255,255,255,0.05)',
        border:       '1px solid rgba(255,255,255,0.1)',
        borderRadius: '14px',
        padding:      '10px 12px',
        transition:   'border-color 0.2s ease',
      }}
        onFocus={() => {}}
        onBlur={() => {}}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder="Ask about ROI, campaigns, audience..."
          rows={1}
          style={{
            flex:       1,
            background: 'transparent',
            border:     'none',
            outline:    'none',
            resize:     'none',
            color:      '#e2e8f0',
            fontSize:   '13px',
            fontFamily: 'Syne, sans-serif',
            lineHeight: '1.6',
            maxHeight:  '100px',
            overflowY:  'auto',
            scrollbarWidth: 'none',
          }}
        />

        <button
          onClick={handleSend}
          disabled={!value.trim() || isLoading}
          style={{
            width:          '34px',
            height:         '34px',
            minWidth:       '34px',
            borderRadius:   '50%',
            background:     (!value.trim() || isLoading)
              ? 'rgba(255,255,255,0.06)'
              : 'linear-gradient(135deg, #0ea5e9, #8b5cf6)',
            border:         'none',
            cursor:         (!value.trim() || isLoading) ? 'not-allowed' : 'pointer',
            display:        'flex',
            alignItems:     'center',
            justifyContent: 'center',
            color:          (!value.trim() || isLoading) ? '#334155' : '#fff',
            fontSize:       '16px',
            transition:     'all 0.2s ease',
            boxShadow:      (!value.trim() || isLoading)
              ? 'none'
              : '0 0 16px rgba(14,165,233,0.4)',
            flexShrink: 0,
          }}
        >
          {isLoading ? '◌' : '↑'}
        </button>
      </div>

      <p style={{
        margin:     '6px 0 0',
        textAlign:  'center',
        fontSize:   '10px',
        color:      '#1e3a5f',
        fontFamily: 'DM Mono, monospace',
      }}>
        Enter to send · Shift+Enter for newline
      </p>
    </div>
  )
}