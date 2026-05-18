/**
 * panels/AlertsPanel.jsx
 *
 * Smart Alerts tab — displays AI-generated critical/warning alerts
 * with severity badges, platform info, metric, message, and action.
 */

export default function AlertsPanel({ alerts }) {
  if (!alerts) return (
    <div style={{
      textAlign: 'center', padding: '80px 0',
      color: '#334155', fontFamily: 'DM Mono, monospace', fontSize: '12px',
    }}>
      Loading alerts...
    </div>
  )

  const { critical_count, warning_count, alerts: alertList = [], platforms_scanned } = alerts

  return (
    <div>
      {/* Summary Cards */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        {[
          {
            label: 'Critical', count: critical_count,
            color: '#f87171', bg: 'rgba(239,68,68,0.08)',
            border: 'rgba(239,68,68,0.2)', icon: '⚠',
          },
          {
            label: 'Warnings', count: warning_count,
            color: '#fbbf24', bg: 'rgba(251,191,36,0.08)',
            border: 'rgba(251,191,36,0.2)', icon: '△',
          },
          {
            label: 'Platforms Scanned', count: platforms_scanned,
            color: '#38bdf8', bg: 'rgba(14,165,233,0.08)',
            border: 'rgba(14,165,233,0.2)', icon: '◈',
          },
        ].map(({ label, count, color, bg, border, icon }) => (
          <div key={label} style={{
            background: bg, border: `1px solid ${border}`,
            borderRadius: '12px', padding: '14px 20px',
            flex: 1, textAlign: 'center',
          }}>
            <div style={{ fontSize: '20px', marginBottom: '4px' }}>{icon}</div>
            <div style={{
              fontSize: '26px', fontWeight: 700,
              color, fontFamily: 'Syne, sans-serif',
            }}>
              {count ?? '—'}
            </div>
            <div style={{
              fontSize: '10px', color: '#475569',
              fontFamily: 'DM Mono, monospace', marginTop: '2px',
            }}>
              {label}
            </div>
          </div>
        ))}
      </div>

      {/* Alert list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {alertList.length === 0 && (
          <div style={{
            textAlign: 'center', padding: '40px',
            color: '#1e3a5f', fontFamily: 'DM Mono, monospace', fontSize: '11px',
          }}>
            No alerts found.
          </div>
        )}
        {alertList.slice(0, 15).map((a, i) => (
          <div key={i} style={{
            background:   a.severity === 'CRITICAL'
              ? 'rgba(239,68,68,0.06)' : 'rgba(251,191,36,0.04)',
            border:       a.severity === 'CRITICAL'
              ? '1px solid rgba(239,68,68,0.18)' : '1px solid rgba(251,191,36,0.12)',
            borderRadius: '10px',
            padding:      '12px 16px',
            display:      'flex', gap: '12px', alignItems: 'flex-start',
          }}>
            <span style={{
              fontSize: '9px', fontFamily: 'DM Mono, monospace',
              padding: '2px 7px', borderRadius: '4px', flexShrink: 0, marginTop: '2px',
              background: a.severity === 'CRITICAL'
                ? 'rgba(239,68,68,0.15)' : 'rgba(251,191,36,0.12)',
              color: a.severity === 'CRITICAL' ? '#f87171' : '#fbbf24',
              letterSpacing: '0.05em',
            }}>
              {a.severity}
            </span>
            <div style={{ flex: 1 }}>
              <div style={{
                fontSize: '12px', color: '#94a3b8',
                fontFamily: 'Syne, sans-serif', marginBottom: '4px',
              }}>
                <strong style={{ color: '#cbd5e1' }}>{a.platform}</strong>
                {a.metric && (
                  <span style={{ color: '#475569', marginLeft: '6px' }}>
                    · {a.metric}
                  </span>
                )}
              </div>
              <div style={{
                fontSize: '11px', color: '#475569',
                fontFamily: 'DM Mono, monospace', lineHeight: 1.6,
              }}>
                {a.message}
              </div>
              {a.action && (
                <div style={{
                  fontSize: '10px', color: '#0ea5e9',
                  fontFamily: 'DM Mono, monospace', marginTop: '5px', opacity: 0.8,
                }}>
                  → {a.action}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}