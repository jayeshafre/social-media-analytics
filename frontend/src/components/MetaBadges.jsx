/**
 * MetaBadges.jsx
 *
 * Small pill badges rendered below each AI response.
 * Shows: intent, platform, confidence, kpi, rag, recs, terms, tokens.
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

function Badge({ bg, text, border, children }) {
  return (
    <span style={{
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
    }}>
      {children}
    </span>
  )
}

export default function MetaBadges({ meta }) {
  if (!meta) return null

  const colors      = INTENT_COLORS[meta.intent] || INTENT_COLORS.general
  const platformIcon = meta.platform ? PLATFORM_ICONS[meta.platform] || '🌐' : null

  return (
    <div style={{
      display:    'flex',
      flexWrap:   'wrap',
      gap:        '6px',
      marginTop:  '12px',
      paddingTop: '10px',
      borderTop:  '1px solid rgba(255,255,255,0.06)',
    }}>

      {/* Intent */}
      <Badge bg={colors.bg} text={colors.text} border={colors.border}>
        ◈ {meta.intent}
      </Badge>

      {/* Platform */}
      {meta.platform && (
        <Badge bg="#0f1923" text="#94a3b8" border="#1e3a5f">
          {platformIcon} {meta.platform}
        </Badge>
      )}

      {/* Confidence */}
      <Badge
        bg={meta.confidence === 'high' ? '#0d2b1a' : '#2a1a0e'}
        text={meta.confidence === 'high' ? '#4ade80' : '#fb923c'}
        border={meta.confidence === 'high' ? '#166534' : '#9a3412'}
      >
        {meta.confidence === 'high' ? '⬤' : '◉'} {meta.confidence}
      </Badge>

      {/* KPI data */}
      {meta.kpiFetched && (
        <Badge bg="#0d1f2e" text="#67e8f9" border="#164e63">
          ▦ kpi data
        </Badge>
      )}

      {/* RAG */}
      {meta.ragFetched && (
        <Badge bg="#1a0d2e" text="#a78bfa" border="#4c1d95">
          ◎ rag
        </Badge>
      )}

      {/* Recommendations */}
      {meta.recCount > 0 && (
        <Badge bg="#1a1a0d" text="#fbbf24" border="#78350f">
          ✦ {meta.recCount} rec{meta.recCount !== 1 ? 's' : ''}
        </Badge>
      )}

      {/* Terms explained */}
      {meta.termsCount > 0 && (
        <Badge bg="#1a150a" text="#fcd34d" border="#92400e">
          ◉ {meta.termsCount} term{meta.termsCount !== 1 ? 's' : ''}
        </Badge>
      )}

      {/* Tokens */}
      <Badge bg="#111" text="#475569" border="#1e293b">
        {meta.tokens?.toLocaleString()} tokens
      </Badge>
    </div>
  )
}