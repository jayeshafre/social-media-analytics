/**
 * shared/FilterBar.jsx
 *
 * Platform icon pills + year pills.
 * Matches the Power BI slicer UX from your dashboard screenshots.
 */

const PLATFORM_META = {
  All:                  { emoji: '◈', color: '#94a3b8' },
  Instagram:            { emoji: '📷', color: '#e1306c' },
  Facebook:             { emoji: '👥', color: '#1877f2' },
  YouTube:              { emoji: '▶', color: '#ff4444'  },
  LinkedIn:             { emoji: '💼', color: '#0a66c2' },
  'WhatsApp Business':  { emoji: '💬', color: '#25d366' },
}

function PlatformPill({ platform, active, onClick }) {
  const meta = PLATFORM_META[platform] || { emoji: '○', color: '#94a3b8' }
  return (
    <button
      onClick={() => onClick(platform)}
      style={{
        padding:      '6px 14px',
        borderRadius: '8px',
        border:       active
          ? `1px solid ${meta.color}55`
          : '1px solid rgba(255,255,255,0.08)',
        background:   active
          ? `${meta.color}18`
          : 'rgba(255,255,255,0.03)',
        color:        active ? meta.color : '#475569',
        fontSize:     '12px',
        fontFamily:   'Syne, sans-serif',
        fontWeight:   active ? 600 : 400,
        cursor:       'pointer',
        display:      'flex',
        alignItems:   'center',
        gap:          '6px',
        transition:   'all 0.15s ease',
        whiteSpace:   'nowrap',
      }}
      onMouseEnter={e => {
        if (!active) {
          e.currentTarget.style.borderColor = `${meta.color}33`
          e.currentTarget.style.color       = '#94a3b8'
        }
      }}
      onMouseLeave={e => {
        if (!active) {
          e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'
          e.currentTarget.style.color       = '#475569'
        }
      }}
    >
      <span style={{ fontSize: '14px' }}>{meta.emoji}</span>
      {platform}
    </button>
  )
}

function YearPill({ year, active, onClick }) {
  return (
    <button
      onClick={() => onClick(year)}
      style={{
        padding:      '5px 12px',
        borderRadius: '7px',
        border:       active
          ? '1px solid rgba(124,58,237,0.5)'
          : '1px solid rgba(255,255,255,0.08)',
        background:   active
          ? 'rgba(124,58,237,0.18)'
          : 'rgba(255,255,255,0.03)',
        color:        active ? '#c4b5fd' : '#475569',
        fontSize:     '11px',
        fontFamily:   'DM Mono, monospace',
        cursor:       'pointer',
        transition:   'all 0.15s ease',
      }}
      onMouseEnter={e => {
        if (!active) {
          e.currentTarget.style.borderColor = 'rgba(124,58,237,0.25)'
          e.currentTarget.style.color       = '#94a3b8'
        }
      }}
      onMouseLeave={e => {
        if (!active) {
          e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'
          e.currentTarget.style.color       = '#475569'
        }
      }}
    >
      {year}
    </button>
  )
}

export default function FilterBar({
  platforms, activePlatform, onPlatformChange,
  years,     activeYear,     onYearChange,
}) {
  return (
    <div style={{
      background:   'rgba(255,255,255,0.02)',
      border:       '1px solid rgba(255,255,255,0.06)',
      borderRadius: '12px',
      padding:      '12px 16px',
      marginBottom: '16px',
      display:      'flex',
      gap:          '20px',
      flexWrap:     'wrap',
      alignItems:   'center',
    }}>
      {/* Platform filter */}
      <div>
        <div style={{
          fontSize: '9px', color: '#334155',
          fontFamily: 'DM Mono, monospace',
          letterSpacing: '0.1em', textTransform: 'uppercase',
          marginBottom: '7px',
        }}>
          Platform
        </div>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {platforms.map(p => (
            <PlatformPill
              key={p} platform={p}
              active={activePlatform === p}
              onClick={onPlatformChange}
            />
          ))}
        </div>
      </div>

      {/* Divider */}
      <div style={{
        width: '1px', alignSelf: 'stretch',
        background: 'rgba(255,255,255,0.06)',
      }} />

      {/* Year filter */}
      <div>
        <div style={{
          fontSize: '9px', color: '#334155',
          fontFamily: 'DM Mono, monospace',
          letterSpacing: '0.1em', textTransform: 'uppercase',
          marginBottom: '7px',
        }}>
          Year
        </div>
        <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
          {years.map(y => (
            <YearPill
              key={y} year={y}
              active={activeYear === y}
              onClick={onYearChange}
            />
          ))}
        </div>
      </div>
    </div>
  )
}