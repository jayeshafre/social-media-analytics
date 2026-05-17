/**
 * ChatMessages.jsx — Full-screen layout version.
 *
 * Messages centred with max-width for readability.
 */

import MessageBubble from './MessageBubble'

const SUGGESTED_QUESTIONS = [
  'Why did Instagram ROI drop last month?',
  'Which platform has the best ROAS this quarter?',
  'Show me audience demographics for Facebook campaigns.',
  'What campaigns should I pause to cut costs?',
  'Detect any anomalies in YouTube engagement.',
  'Compare LinkedIn vs Instagram conversion rates.',
]

export default function ChatMessages({ messages, isLoading, bottomRef, onSuggest }) {
  return (
    <div style={{
      flex:       1,
      overflowY:  'auto',
      padding:    '40px 24px 16px',
      scrollbarWidth: 'thin',
      scrollbarColor: '#0f2744 transparent',
    }}>
      <div style={{ maxWidth: '760px', margin: '0 auto' }}>

        {/* ── Welcome state ─────────────────────────── */}
        {messages.length === 0 && !isLoading && (
          <div style={{ paddingTop: '60px', animation: 'fadeInUp 0.5s ease-out' }}>
            <div style={{
              width:          '64px',
              height:         '64px',
              borderRadius:   '18px',
              background:     'linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%)',
              margin:         '0 auto 24px',
              display:        'flex',
              alignItems:     'center',
              justifyContent: 'center',
              fontSize:       '28px',
              boxShadow:      '0 0 48px rgba(14,165,233,0.35)',
            }}>◈</div>

            <h2 style={{
              textAlign:     'center',
              color:         '#f1f5f9',
              fontFamily:    'Syne, sans-serif',
              fontWeight:    800,
              fontSize:      '26px',
              margin:        '0 0 10px',
              letterSpacing: '-0.02em',
            }}>
              What do you want to know?
            </h2>

            <p style={{
              textAlign:  'center',
              color:      '#334155',
              fontFamily: 'DM Mono, monospace',
              fontSize:   '12px',
              margin:     '0 0 48px',
              lineHeight: 1.7,
            }}>
              Powered by real KPI data · RAG knowledge · ML predictions
            </p>

            <div style={{
              display:             'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap:                 '10px',
            }}>
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button key={i} onClick={() => onSuggest(q)}
                  style={{
                    background:   'rgba(255,255,255,0.03)',
                    border:       '1px solid rgba(255,255,255,0.07)',
                    borderRadius: '12px',
                    padding:      '14px 16px',
                    color:        '#475569',
                    fontSize:     '12.5px',
                    fontFamily:   'Syne, sans-serif',
                    cursor:       'pointer',
                    textAlign:    'left',
                    lineHeight:   1.55,
                    transition:   'all 0.18s ease',
                    display:      'flex',
                    alignItems:   'flex-start',
                    gap:          '8px',
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.background  = 'rgba(14,165,233,0.08)'
                    e.currentTarget.style.borderColor = 'rgba(14,165,233,0.25)'
                    e.currentTarget.style.color       = '#cbd5e1'
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.background  = 'rgba(255,255,255,0.03)'
                    e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)'
                    e.currentTarget.style.color       = '#475569'
                  }}
                >
                  <span style={{ color: '#1e3a5f', fontSize: '14px', flexShrink: 0 }}>↗</span>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map(msg => <MessageBubble key={msg.id} message={msg} />)}

        {/* Typing indicator */}
        {isLoading && (
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', marginBottom: '20px' }}>
            <div style={{
              width: '36px', height: '36px', minWidth: '36px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #0ea5e9, #7c3aed)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '13px', color: '#fff', fontFamily: 'Syne, sans-serif', fontWeight: 700,
              boxShadow: '0 0 14px rgba(14,165,233,0.3)',
            }}>AI</div>
            <div style={{
              background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)',
              borderRadius: '4px 16px 16px 16px', padding: '18px 22px',
              display: 'flex', gap: '6px', alignItems: 'center',
            }}>
              {[0, 1, 2].map(i => (
                <span key={i} style={{
                  width: '7px', height: '7px', borderRadius: '50%', background: '#0ea5e9',
                  display: 'inline-block',
                  animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
                }} />
              ))}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}