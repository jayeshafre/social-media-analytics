/**
 * shared/ChartCard.jsx
 *
 * Wrapper for every chart panel.
 * Supports click-to-drill-down — shows a ↗ expand hint on hover.
 *
 * Props:
 *   title      - chart title
 *   subtitle   - muted description
 *   children   - chart content
 *   fullWidth  - spans 2 grid columns
 *   onClick    - drill-down handler
 *   badge      - optional badge text (e.g. "LIVE")
 *   noPad      - removes padding for treemap-style charts
 */

export default function ChartCard({
  title, subtitle, children,
  fullWidth, onClick, badge, noPad,
}) {
  return (
    <div
      onClick={onClick}
      style={{
        background:   'rgba(255,255,255,0.03)',
        border:       '1px solid rgba(255,255,255,0.07)',
        borderRadius: '14px',
        padding:      noPad ? '16px 18px 0' : '16px 18px',
        gridColumn:   fullWidth ? '1 / -1' : undefined,
        cursor:       onClick ? 'pointer' : 'default',
        transition:   'border-color 0.18s ease, background 0.18s ease',
        position:     'relative',
      }}
      onMouseEnter={e => {
        if (onClick) {
          e.currentTarget.style.borderColor = 'rgba(14,165,233,0.25)'
          e.currentTarget.style.background  = 'rgba(14,165,233,0.03)'
        }
      }}
      onMouseLeave={e => {
        if (onClick) {
          e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)'
          e.currentTarget.style.background  = 'rgba(255,255,255,0.03)'
        }
      }}
    >
      <div style={{
        display: 'flex', alignItems: 'flex-start',
        justifyContent: 'space-between', marginBottom: '12px',
      }}>
        <div>
          <div style={{
            fontSize: '12px', fontWeight: 600,
            color: '#cbd5e1', fontFamily: 'Syne, sans-serif',
          }}>
            {title}
          </div>
          {subtitle && (
            <div style={{
              fontSize: '10px', color: '#334155',
              fontFamily: 'DM Mono, monospace', marginTop: '2px',
            }}>
              {subtitle}
            </div>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {badge && (
            <span style={{
              fontSize: '9px', fontFamily: 'DM Mono, monospace',
              padding: '2px 7px', borderRadius: '4px',
              background: 'rgba(14,165,233,0.1)',
              border: '1px solid rgba(14,165,233,0.2)',
              color: '#38bdf8', letterSpacing: '0.05em',
            }}>
              {badge}
            </span>
          )}
          {onClick && (
            <span style={{
              fontSize: '11px', color: '#1e3a5f',
              fontFamily: 'DM Mono, monospace',
            }}>
              ↗
            </span>
          )}
        </div>
      </div>
      {children}
    </div>
  )
}