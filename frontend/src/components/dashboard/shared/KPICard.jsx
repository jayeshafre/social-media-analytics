/**
 * shared/KPICard.jsx
 *
 * Reusable KPI card. Matches your dark theme exactly.
 * Supports: sparkline mini-chart, trend indicator, click to drill-down.
 *
 * Props:
 *   label       - string (e.g. "TOTAL REVENUE")
 *   value       - string (e.g. "₹1.67Cr")
 *   sub         - string (e.g. "▲ 18.6% vs last year")
 *   subColor    - hex color for sub text
 *   icon        - emoji or unicode char
 *   iconBg      - background color for icon circle
 *   sparkData   - array of numbers for mini sparkline
 *   sparkColor  - hex for sparkline stroke
 *   onClick     - fn called when card is clicked
 *   active      - bool, highlights card border
 */

import { useEffect, useRef } from 'react'

function MiniSparkline({ data, color = '#0ea5e9' }) {
  const ref = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length) return
    const canvas = ref.current
    const ctx    = canvas.getContext('2d')
    const W = canvas.width
    const H = canvas.height
    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1

    ctx.clearRect(0, 0, W, H)
    ctx.beginPath()
    data.forEach((v, i) => {
      const x = (i / (data.length - 1)) * W
      const y = H - ((v - min) / range) * H * 0.85 - H * 0.05
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    })
    ctx.strokeStyle = color
    ctx.lineWidth   = 1.5
    ctx.stroke()
  }, [data, color])

  if (!data?.length) return null
  return (
    <canvas
      ref={ref}
      width={72}
      height={32}
      style={{ display: 'block', opacity: 0.8 }}
      aria-hidden="true"
    />
  )
}

export default function KPICard({
  label, value, sub, subColor,
  icon, iconBg,
  sparkData, sparkColor,
  onClick, active,
}) {
  return (
    <div
      onClick={onClick}
      style={{
        background:    'rgba(255,255,255,0.03)',
        border:        active
          ? '1px solid rgba(14,165,233,0.45)'
          : '1px solid rgba(255,255,255,0.07)',
        borderRadius:  '12px',
        padding:       '14px 16px',
        cursor:        onClick ? 'pointer' : 'default',
        transition:    'all 0.18s ease',
        position:      'relative',
        overflow:      'hidden',
        boxShadow:     active ? '0 0 20px rgba(14,165,233,0.08)' : 'none',
      }}
      onMouseEnter={e => {
        if (onClick) {
          e.currentTarget.style.border       = '1px solid rgba(14,165,233,0.3)'
          e.currentTarget.style.background   = 'rgba(14,165,233,0.05)'
          e.currentTarget.style.transform    = 'translateY(-1px)'
        }
      }}
      onMouseLeave={e => {
        if (onClick) {
          e.currentTarget.style.border     = active
            ? '1px solid rgba(14,165,233,0.45)'
            : '1px solid rgba(255,255,255,0.07)'
          e.currentTarget.style.background = 'rgba(255,255,255,0.03)'
          e.currentTarget.style.transform  = 'none'
        }
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div style={{ flex: 1 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px',
          }}>
            {icon && (
              <div style={{
                width: '22px', height: '22px', borderRadius: '6px',
                background: iconBg || 'rgba(14,165,233,0.12)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '12px',
              }}>
                {icon}
              </div>
            )}
            <div style={{
              fontSize: '10px', color: '#475569',
              fontFamily: 'DM Mono, monospace', letterSpacing: '0.06em',
              textTransform: 'uppercase',
            }}>
              {label}
            </div>
          </div>
          <div style={{
            fontSize: '22px', fontWeight: 700,
            color: '#f1f5f9', fontFamily: 'Syne, sans-serif', lineHeight: 1.2,
          }}>
            {value}
          </div>
          {sub && (
            <div style={{
              fontSize: '10px', color: subColor || '#475569',
              fontFamily: 'DM Mono, monospace', marginTop: '4px',
            }}>
              {sub}
            </div>
          )}
        </div>
        {sparkData && (
          <div style={{ marginLeft: '8px', alignSelf: 'flex-end', paddingBottom: '2px' }}>
            <MiniSparkline data={sparkData} color={sparkColor} />
          </div>
        )}
      </div>
      {onClick && (
        <div style={{
          position: 'absolute', bottom: '8px', right: '10px',
          fontSize: '9px', color: '#1e3a5f', fontFamily: 'DM Mono, monospace',
        }}>
          click to expand →
        </div>
      )}
    </div>
  )
}