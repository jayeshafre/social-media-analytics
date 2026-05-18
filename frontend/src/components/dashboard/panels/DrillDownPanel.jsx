/**
 * panels/DrillDownPanel.jsx
 *
 * Slide-in panel that appears from the right when user clicks
 * a KPI card or chart. Shows detailed breakdown for that item.
 * Power BI-style "click for details" UX.
 *
 * Props:
 *   panel     - { type, title, subtitle, rows, columns, note }
 *   onClose   - fn
 */

import { useEffect, useRef } from 'react'

const fmt = {
  currency: v => {
    const n = parseFloat(v) || 0
    return n >= 1e7
      ? '₹' + (n / 1e7).toFixed(2) + ' Cr'
      : n >= 1e6
        ? '₹' + (n / 1e6).toFixed(2) + 'M'
        : '₹' + n.toLocaleString('en-IN')
  },
  pct:  v => (parseFloat(v) * 100).toFixed(2) + '%',
  pct2: v => parseFloat(v).toFixed(2) + '%',
  roas: v => parseFloat(v).toFixed(2) + 'x',
  num:  v => Number(parseFloat(v).toFixed(0)).toLocaleString('en-IN'),
  raw:  v => String(v ?? '—'),
}

function BarMini({ value, max, color = '#0ea5e9' }) {
  const pct = Math.min(100, Math.max(0, (parseFloat(value) / (max || 1)) * 100))
  return (
    <div style={{
      height: '5px', borderRadius: '3px',
      background: 'rgba(255,255,255,0.05)',
      marginTop: '3px',
    }}>
      <div style={{
        height: '100%', width: `${pct}%`,
        background: color, borderRadius: '3px',
        transition: 'width 0.4s ease',
      }} />
    </div>
  )
}

export default function DrillDownPanel({ panel, onClose }) {
  const ref = useRef(null)

  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) onClose()
    }
    if (panel) {
      setTimeout(() => document.addEventListener('mousedown', handler), 100)
    }
    return () => document.removeEventListener('mousedown', handler)
  }, [panel, onClose])

  if (!panel) return null

  const { title, subtitle, rows = [], columns = [], note, highlight } = panel

  // Find max values per numeric column for bar rendering
  const maxByCol = {}
  columns.forEach(col => {
    if (col.bar) {
      maxByCol[col.key] = Math.max(...rows.map(r => parseFloat(r[col.key]) || 0))
    }
  })

  return (
    <>
      {/* Backdrop */}
      <div style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.3)',
        zIndex: 100, backdropFilter: 'blur(2px)',
      }} onClick={onClose} />

      {/* Panel */}
      <div
        ref={ref}
        style={{
          position:      'fixed',
          top:           0,
          right:         0,
          bottom:        0,
          width:         '460px',
          background:    '#080d18',
          borderLeft:    '1px solid rgba(255,255,255,0.08)',
          zIndex:        101,
          display:       'flex',
          flexDirection: 'column',
          animation:     'slideInRight 0.22s ease',
          overflow:      'hidden',
        }}
      >
        {/* Header */}
        <div style={{
          padding:      '18px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.07)',
          display:      'flex',
          alignItems:   'flex-start',
          justifyContent: 'space-between',
          flexShrink:   0,
        }}>
          <div>
            <div style={{
              fontSize: '14px', fontWeight: 700,
              color: '#f1f5f9', fontFamily: 'Syne, sans-serif',
            }}>
              {title}
            </div>
            {subtitle && (
              <div style={{
                fontSize: '10px', color: '#475569',
                fontFamily: 'DM Mono, monospace', marginTop: '3px',
              }}>
                {subtitle}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.08)',
              color: '#64748b', cursor: 'pointer',
              width: '28px', height: '28px', borderRadius: '7px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '14px', flexShrink: 0,
            }}
            onMouseEnter={e => {
              e.currentTarget.style.color = '#f87171'
              e.currentTarget.style.borderColor = 'rgba(239,68,68,0.3)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.color = '#64748b'
              e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'
            }}
          >×</button>
        </div>

        {/* Highlight stats */}
        {highlight?.length > 0 && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${highlight.length}, 1fr)`,
            gap: '1px',
            background: 'rgba(255,255,255,0.04)',
            borderBottom: '1px solid rgba(255,255,255,0.07)',
            flexShrink: 0,
          }}>
            {highlight.map((h, i) => (
              <div key={i} style={{
                padding: '12px 16px',
                background: '#080d18',
              }}>
                <div style={{
                  fontSize: '9px', color: '#334155',
                  fontFamily: 'DM Mono, monospace', marginBottom: '4px',
                  textTransform: 'uppercase', letterSpacing: '0.06em',
                }}>
                  {h.label}
                </div>
                <div style={{
                  fontSize: '18px', fontWeight: 700,
                  color: h.color || '#f1f5f9', fontFamily: 'Syne, sans-serif',
                }}>
                  {h.value}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Table */}
        <div style={{
          flex: 1, overflowY: 'auto',
          padding: '16px 20px',
          scrollbarWidth: 'thin',
          scrollbarColor: '#0f2744 transparent',
        }}>
          {rows.length === 0 ? (
            <div style={{
              textAlign: 'center', padding: '40px',
              color: '#334155', fontFamily: 'DM Mono, monospace', fontSize: '11px',
            }}>
              No data available
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  {columns.map(col => (
                    <th key={col.key} style={{
                      fontSize: '9px', color: '#334155',
                      fontFamily: 'DM Mono, monospace',
                      textTransform: 'uppercase', letterSpacing: '0.07em',
                      padding: '6px 10px 8px',
                      textAlign: col.align || 'left',
                      borderBottom: '1px solid rgba(255,255,255,0.06)',
                      whiteSpace: 'nowrap',
                    }}>
                      {col.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr
                    key={i}
                    style={{
                      background: i % 2 === 0
                        ? 'transparent'
                        : 'rgba(255,255,255,0.015)',
                    }}
                  >
                    {columns.map(col => {
                      const raw = row[col.key]
                      let display = raw
                      if (col.format === 'currency') display = fmt.currency(raw)
                      else if (col.format === 'pct')  display = fmt.pct(raw)
                      else if (col.format === 'pct2') display = fmt.pct2(raw)
                      else if (col.format === 'roas') display = fmt.roas(raw)
                      else if (col.format === 'num')  display = fmt.num(raw)
                      else display = fmt.raw(raw)

                      return (
                        <td key={col.key} style={{
                          padding: '8px 10px',
                          fontSize: '11px',
                          fontFamily: col.mono ? 'DM Mono, monospace' : 'Syne, sans-serif',
                          color: col.color
                            ? (typeof col.color === 'function' ? col.color(raw) : col.color)
                            : (col.key === columns[0].key ? '#cbd5e1' : '#64748b'),
                          textAlign: col.align || 'left',
                          borderBottom: '1px solid rgba(255,255,255,0.04)',
                        }}>
                          {col.bar ? (
                            <>
                              {display}
                              <BarMini
                                value={raw}
                                max={maxByCol[col.key]}
                                color={col.barColor || '#0ea5e9'}
                              />
                            </>
                          ) : display}
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {note && (
            <div style={{
              marginTop: '16px', padding: '10px 14px',
              background: 'rgba(14,165,233,0.04)',
              border: '1px solid rgba(14,165,233,0.1)',
              borderRadius: '8px',
              fontSize: '10px', color: '#475569',
              fontFamily: 'DM Mono, monospace', lineHeight: 1.6,
            }}>
              ℹ {note}
            </div>
          )}
        </div>
      </div>
    </>
  )
}