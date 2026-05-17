/**
 * MetaBadges.jsx
 *
 * Small pill badges rendered below each AI response.
 * Shows: intent category, platform detected, confidence, token count.
 * Gives the user visibility into what the AI "understood" about their question.
 */

const INTENT_COLORS = {
  revenue:    { bg: '#0d2b1a', text: '#4ade80', border: '#166534' },
  campaign:   { bg: '#1a1a2e', text: '#818cf8', border: '#3730a3' },
  audience:   { bg: '#2a1a0e', text: '#fb923c', border: '#9a3412' },
  platform:   { bg: '#0e1a2e', text: '#38bdf8', border: '#075985' },
  engagement: { bg: '#1a0e2e', text: '#c084fc', border: '#6b21a8' },
  anomaly:    { bg: '#2e0e0e', text: '#f87171', border: '#991b1b' },
  general:    { bg: '#1a1a1a', text: '#94a3b8', border: '#334155' },
}

const PLATFORM_ICONS = {
  Instagram: '📸',
  Facebook:  '📘',
  YouTube:   '▶️',
  LinkedIn:  '💼',
  WhatsApp:  '💬',
}

export default function MetaBadges({ meta }) {
  if (!meta) return null

  const colors = INTENT_COLORS[meta.intent] || INTENT_COLORS.general
  const platformIcon = meta.platform ? PLATFORM_ICONS[meta.platform] || '🌐' : null

  const badgeStyle = (bg, text, border) => ({
    display:         'inline-flex',
    alignItems:      'center',
    gap:             '4px',
    padding:         '2px 8px',
    borderRadius:    '999px',
    fontSize:        '10px',
    fontFamily:      'DM Mono, monospace',
    letterSpacing:   '0.04em',
    backgroundColor: bg,
    color:           text,
    border:          `1px solid ${border}`,
    whiteSpace:      'nowrap',
  })

  return (
    <div style={{
      display:    'flex',
      flexWrap:   'wrap',
      gap:        '6px',
      marginTop:  '10px',
      paddingTop: '8px',
      borderTop:  '1px solid rgba(255,255,255,0.06)',
    }}>

      {/* Intent */}
      <span style={badgeStyle(colors.bg, colors.text, colors.border)}>
        ◈ {meta.intent}
      </span>

      {/* Platform */}
      {meta.platform && (
        <span style={badgeStyle('#0f1923', '#94a3b8', '#1e3a5f')}>
          {platformIcon} {meta.platform}
        </span>
      )}

      {/* Confidence */}
      <span style={badgeStyle(
        meta.confidence === 'high' ? '#0d2b1a' : '#2a1a0e',
        meta.confidence === 'high' ? '#4ade80' : '#fb923c',
        meta.confidence === 'high' ? '#166534' : '#9a3412',
      )}>
        {meta.confidence === 'high' ? '⬤' : '◉'} {meta.confidence}
      </span>

      {/* KPI data */}
      {meta.kpiFetched && (
        <span style={badgeStyle('#0d1f2e', '#67e8f9', '#164e63')}>
          ▦ kpi data
        </span>
      )}

      {/* RAG */}
      {meta.ragFetched && (
        <span style={badgeStyle('#1a0d2e', '#a78bfa', '#4c1d95')}>
          ◎ rag
        </span>
      )}

      {/* Recommendations */}
      {meta.recCount > 0 && (
        <span style={badgeStyle('#1a1a0d', '#fbbf24', '#78350f')}>
          ✦ {meta.recCount} rec{meta.recCount !== 1 ? 's' : ''}
        </span>
      )}

      {/* Tokens */}
      <span style={badgeStyle('#111', '#475569', '#1e293b')}>
        {meta.tokens?.toLocaleString()} tokens
      </span>
    </div>
  )
}