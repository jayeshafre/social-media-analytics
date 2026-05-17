/**
 * DashboardView.jsx
 *
 * Live marketing intelligence dashboard.
 * Replaces the Superset iframe in App.jsx.
 *
 * Matches your existing dark theme exactly:
 * - #080d18 background
 * - #0ea5e9 accent
 * - Syne + DM Mono fonts
 * - Same inline style pattern as all other components
 *
 * Loads Chart.js from CDN once on mount.
 * All data comes from your FastAPI backend.
 */

import { useEffect, useState } from 'react'
import { useDashboard } from '../../hooks/useDashboard'
import {
  RevenueByPlatformChart,
  MonthlyRevenueChart,
  ROASChart,
  CTRByCampaignChart,
  FunnelChart,
  AudienceAgeChart,
} from './DashboardCharts'

// ── Load Chart.js from CDN once ───────────────────────────────
function useChartJS() {
  const [ready, setReady] = useState(!!window.Chart)

  useEffect(() => {
    if (window.Chart) { setReady(true); return }
    const script    = document.createElement('script')
    script.src      = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js'
    script.onload   = () => setReady(true)
    script.onerror  = () => console.error('Chart.js failed to load')
    document.head.appendChild(script)
  }, [])

  return ready
}

// ── KPI Card ──────────────────────────────────────────────────
function KPICard({ label, value, sub, subColor }) {
  return (
    <div style={{
      background:   'rgba(255,255,255,0.03)',
      border:       '1px solid rgba(255,255,255,0.07)',
      borderRadius: '12px',
      padding:      '14px 16px',
    }}>
      <div style={{
        fontSize:     '10px',
        color:        '#475569',
        fontFamily:   'DM Mono, monospace',
        marginBottom: '6px',
        letterSpacing:'0.04em',
      }}>{label}</div>
      <div style={{
        fontSize:   '22px',
        fontWeight: 600,
        color:      '#f1f5f9',
        fontFamily: 'Syne, sans-serif',
        lineHeight: 1.2,
      }}>{value}</div>
      {sub && (
        <div style={{
          fontSize:   '10px',
          color:      subColor || '#475569',
          fontFamily: 'DM Mono, monospace',
          marginTop:  '4px',
        }}>{sub}</div>
      )}
    </div>
  )
}

// ── Platform filter pills ─────────────────────────────────────
function PlatformFilter({ platforms, active, onChange }) {
  return (
    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', alignItems: 'center' }}>
      <span style={{
        fontSize:   '10px',
        color:      '#334155',
        fontFamily: 'DM Mono, monospace',
        marginRight:'4px',
      }}>Platform:</span>
      {platforms.map(p => (
        <button
          key={p}
          onClick={() => onChange(p)}
          style={{
            padding:      '4px 12px',
            borderRadius: '999px',
            border:       active === p
              ? '1px solid rgba(14,165,233,0.5)'
              : '1px solid rgba(255,255,255,0.08)',
            background:   active === p
              ? 'rgba(14,165,233,0.15)'
              : 'rgba(255,255,255,0.03)',
            color:        active === p ? '#38bdf8' : '#475569',
            fontSize:     '11px',
            fontFamily:   'DM Mono, monospace',
            cursor:       'pointer',
            transition:   'all 0.15s ease',
          }}
          onMouseEnter={e => {
            if (active !== p) {
              e.currentTarget.style.borderColor = 'rgba(14,165,233,0.25)'
              e.currentTarget.style.color       = '#94a3b8'
            }
          }}
          onMouseLeave={e => {
            if (active !== p) {
              e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'
              e.currentTarget.style.color       = '#475569'
            }
          }}
        >
          {p}
        </button>
      ))}
    </div>
  )
}

// ── Tab bar ───────────────────────────────────────────────────
function TabBar({ active, onChange }) {
  const tabs = [
    { id: 'overview',  label: '▦ Overview'  },
    { id: 'campaigns', label: '◈ Campaigns' },
    { id: 'audience',  label: '◉ Audience'  },
    { id: 'alerts',    label: '⚡ Alerts'    },
  ]
  return (
    <div style={{ display: 'flex', gap: '4px' }}>
      {tabs.map(t => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          style={{
            padding:      '7px 14px',
            borderRadius: '8px',
            border:       active === t.id
              ? '1px solid rgba(14,165,233,0.3)'
              : '1px solid transparent',
            background:   active === t.id
              ? 'rgba(14,165,233,0.1)'
              : 'transparent',
            color:        active === t.id ? '#38bdf8' : '#475569',
            fontSize:     '11px',
            fontFamily:   'Syne, sans-serif',
            fontWeight:   active === t.id ? 600 : 400,
            cursor:       'pointer',
            transition:   'all 0.15s ease',
          }}
        >
          {t.label}
        </button>
      ))}
    </div>
  )
}

// ── Alerts panel ──────────────────────────────────────────────
function AlertsPanel({ alerts }) {
  if (!alerts) return (
    <div style={{
      textAlign:'center', padding:'60px 0',
      color:'#334155', fontFamily:'DM Mono, monospace', fontSize:'12px',
    }}>Loading alerts...</div>
  )

  const { critical_count, warning_count, alerts: alertList = [] } = alerts

  return (
    <div>
      <div style={{ display:'flex', gap:'12px', marginBottom:'20px' }}>
        {[
          { label: 'Critical', count: critical_count, color: '#f87171', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.2)' },
          { label: 'Warnings', count: warning_count,  color: '#fbbf24', bg: 'rgba(251,191,36,0.08)', border: 'rgba(251,191,36,0.2)' },
          { label: 'Platforms', count: alerts.platforms_scanned, color: '#38bdf8', bg: 'rgba(14,165,233,0.08)', border: 'rgba(14,165,233,0.2)' },
        ].map(({ label, count, color, bg, border }) => (
          <div key={label} style={{
            background: bg, border: `1px solid ${border}`,
            borderRadius:'10px', padding:'12px 16px', flex:1, textAlign:'center',
          }}>
            <div style={{ fontSize:'22px', fontWeight:600, color, fontFamily:'Syne, sans-serif' }}>
              {count}
            </div>
            <div style={{ fontSize:'10px', color:'#475569', fontFamily:'DM Mono, monospace', marginTop:'2px' }}>
              {label}
            </div>
          </div>
        ))}
      </div>

      <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
        {alertList.slice(0, 12).map((a, i) => (
          <div key={i} style={{
            background:   a.severity === 'CRITICAL'
              ? 'rgba(239,68,68,0.06)'
              : 'rgba(251,191,36,0.04)',
            border:       a.severity === 'CRITICAL'
              ? '1px solid rgba(239,68,68,0.18)'
              : '1px solid rgba(251,191,36,0.15)',
            borderRadius: '10px',
            padding:      '10px 14px',
            display:      'flex',
            gap:          '12px',
            alignItems:   'flex-start',
          }}>
            <span style={{
              fontSize:   '9px',
              fontFamily: 'DM Mono, monospace',
              padding:    '2px 6px',
              borderRadius:'4px',
              background: a.severity === 'CRITICAL' ? 'rgba(239,68,68,0.15)' : 'rgba(251,191,36,0.12)',
              color:      a.severity === 'CRITICAL' ? '#f87171' : '#fbbf24',
              flexShrink: 0,
              marginTop:  '1px',
            }}>{a.severity}</span>
            <div style={{ flex:1 }}>
              <div style={{
                fontSize:   '12px',
                color:      '#94a3b8',
                fontFamily: 'Syne, sans-serif',
                marginBottom:'3px',
              }}>
                <strong style={{ color:'#cbd5e1' }}>{a.platform}</strong> · {a.metric}
              </div>
              <div style={{
                fontSize:   '11px',
                color:      '#475569',
                fontFamily: 'DM Mono, monospace',
                lineHeight: 1.5,
              }}>{a.message}</div>
              <div style={{
                fontSize:   '10px',
                color:      '#0ea5e9',
                fontFamily: 'DM Mono, monospace',
                marginTop:  '4px',
                opacity:    0.7,
              }}>→ {a.action}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Loading skeleton ──────────────────────────────────────────
function LoadingSkeleton() {
  return (
    <div style={{ padding: '0 20px' }}>
      {[1,2,3].map(i => (
        <div key={i} style={{
          height: '120px',
          background: 'rgba(255,255,255,0.03)',
          borderRadius: '12px',
          marginBottom: '12px',
          animation: 'pulse 1.5s ease-in-out infinite',
        }} />
      ))}
    </div>
  )
}

// ── Error state ───────────────────────────────────────────────
function ErrorState({ error, onRetry }) {
  return (
    <div style={{
      display:'flex', flexDirection:'column', alignItems:'center',
      justifyContent:'center', height:'60vh', gap:'16px',
    }}>
      <div style={{ fontSize:'32px', opacity:0.3 }}>⚠</div>
      <div style={{
        color:'#f87171', fontFamily:'DM Mono, monospace', fontSize:'12px',
        textAlign:'center', maxWidth:'400px', lineHeight:1.6,
      }}>
        {error || 'Failed to load dashboard data'}
      </div>
      <button onClick={onRetry} style={{
        padding:'8px 20px', borderRadius:'8px',
        background:'rgba(14,165,233,0.1)', border:'1px solid rgba(14,165,233,0.25)',
        color:'#38bdf8', fontFamily:'DM Mono, monospace', fontSize:'11px', cursor:'pointer',
      }}>
        Try Again
      </button>
    </div>
  )
}

// ── Main DashboardView ────────────────────────────────────────
export default function DashboardView() {
  const chartJSReady = useChartJS()

  const {
    activePlatform, activeTab, isLoading, lastRefreshed,
    error, platforms, revenueByPlatform, monthlyRevenue,
    campaignData, audienceData, funnelData, alerts, forecast,
    kpis, setActiveTab, handlePlatformChange, refresh,
  } = useDashboard()

  const fmt = {
    currency: v => v >= 1e7
      ? '₹' + (v / 1e7).toFixed(1) + 'Cr'
      : '₹' + (v / 1e6).toFixed(1) + 'M',
    roas:     v => v.toFixed(2) + 'x',
    roi:      v => (v * 100).toFixed(1) + '%',
    count: v => v >= 1000 ? Math.round(v / 1000) + 'K' : Math.round(v).toString(),
  }

  return (
    <div style={{
      flex:          1,
      height:        '100vh',
      display:       'flex',
      flexDirection: 'column',
      background:    'linear-gradient(160deg, #080d18 0%, #050a12 50%, #080d18 100%)',
      overflow:      'hidden',
      position:      'relative',
    }}>

      {/* Grid texture — matches ChatPanel exactly */}
      <div style={{
        position:   'absolute', inset: 0,
        backgroundImage: `
          linear-gradient(rgba(14,165,233,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(14,165,233,0.03) 1px, transparent 1px)
        `,
        backgroundSize: '48px 48px',
        pointerEvents: 'none', zIndex: 0,
      }} />

      {/* ── Top bar ─────────────────────────────────── */}
      <div style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        padding:        '14px 24px',
        borderBottom:   '1px solid rgba(255,255,255,0.055)',
        flexShrink:     0,
        zIndex:         1,
        backdropFilter: 'blur(8px)',
        background:     'rgba(5,10,18,0.6)',
      }}>
        <div style={{ display:'flex', alignItems:'center', gap:'10px' }}>
          <span style={{
            fontSize:'14px', fontFamily:'Syne, sans-serif',
            fontWeight:700, color:'#f1f5f9',
          }}>Marketing Intelligence</span>
          <span style={{
            fontSize:'10px', fontFamily:'DM Mono, monospace',
            color:'#334155', letterSpacing:'0.04em',
          }}>Live · PostgreSQL</span>
        </div>

        <div style={{ display:'flex', gap:'8px', alignItems:'center' }}>
          {lastRefreshed && (
            <span style={{
              fontSize:'10px', color:'#334155',
              fontFamily:'DM Mono, monospace',
            }}>
              Updated {lastRefreshed.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' })}
            </span>
          )}
          <button
            onClick={refresh}
            disabled={isLoading}
            style={{
              padding:'5px 12px', borderRadius:'8px',
              background:'rgba(255,255,255,0.04)',
              border:'1px solid rgba(255,255,255,0.08)',
              color: isLoading ? '#334155' : '#64748b',
              fontFamily:'DM Mono, monospace', fontSize:'10px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition:'all 0.15s ease',
            }}
          >
            {isLoading ? '◌ Loading...' : '↺ Refresh'}
          </button>
        </div>
      </div>

      {/* ── Filter + tab bar ─────────────────────────── */}
      <div style={{
        padding:      '10px 24px',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        display:      'flex',
        alignItems:   'center',
        justifyContent:'space-between',
        flexShrink:   0,
        zIndex:       1,
        flexWrap:     'wrap',
        gap:          '10px',
      }}>
        <PlatformFilter
          platforms={platforms}
          active={activePlatform}
          onChange={handlePlatformChange}
        />
        <TabBar active={activeTab} onChange={setActiveTab} />
      </div>

      {/* ── Scrollable content ───────────────────────── */}
      <div style={{
        flex:      1,
        overflowY: 'auto',
        padding:   '16px 24px 24px',
        zIndex:    1,
        scrollbarWidth: 'thin',
        scrollbarColor: '#0f2744 transparent',
      }}>
        {error && <ErrorState error={error} onRetry={refresh} />}

        {!error && isLoading && <LoadingSkeleton />}

        {!error && !isLoading && (
          <>
            {/* ── KPI Cards ─────────────────────────── */}
            <div style={{
              display:             'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap:                 '10px',
              marginBottom:        '16px',
            }}>
              <KPICard
                label="TOTAL REVENUE"
                value={kpis ? fmt.currency(kpis.totalRevenue) : '—'}
                sub={activePlatform === 'All' ? 'All platforms' : activePlatform}
              />
              <KPICard
                label="AVG ROAS"
                value={kpis ? fmt.roas(kpis.avgROAS) : '—'}
                sub="Return on ad spend"
              />
              <KPICard
                label="TOTAL AD SPEND"
                value={kpis ? fmt.currency(kpis.totalSpend) : '—'}
                sub="Invested in ads"
              />
              <KPICard
                label="CAMPAIGNS RUN"
                value={kpis ? fmt.count(kpis.totalCampaigns) : '—'}
                sub="Total campaigns"
              />
            </div>

            {/* ── ML Forecast strip ─────────────────── */}
            {forecast?.forecasts && (
              <div style={{
                background:   'rgba(14,165,233,0.04)',
                border:       '1px solid rgba(14,165,233,0.12)',
                borderRadius: '10px',
                padding:      '10px 16px',
                marginBottom: '16px',
                display:      'flex',
                gap:          '8px',
                flexWrap:     'wrap',
                alignItems:   'center',
              }}>
                <span style={{
                  fontSize:'10px', color:'#0ea5e9',
                  fontFamily:'DM Mono, monospace', marginRight:'4px',
                }}>
                  ◈ ML Forecast · {forecast.next_period}:
                </span>
                {[
                  ['avg_roi',     'ROI',     '',  'x'],
                  ['avg_roas',    'ROAS',    '',  'x'],
                  ['total_revenue','Revenue','₹', 'M'],
                ].map(([key, label, pre, suf]) => {
                  const f = forecast.forecasts[key]
                  if (!f || f.error) return null
                  const isUp = f.predicted_value >= f.current_value
                  return (
                    <span key={key} style={{
                      background:'rgba(255,255,255,0.04)',
                      border:'1px solid rgba(255,255,255,0.07)',
                      borderRadius:'6px', padding:'3px 10px',
                      fontSize:'10px', fontFamily:'DM Mono, monospace',
                      color:'#94a3b8',
                    }}>
                      {label}: <span style={{ color: isUp ? '#4ade80' : '#f87171' }}>
                        {isUp ? '▲' : '▼'} {pre}
                        {key === 'total_revenue'
                          ? (f.predicted_value / 1e6).toFixed(1) + suf
                          : f.predicted_value.toFixed(2) + suf
                        }
                      </span>
                    </span>
                  )
                })}
              </div>
            )}

            {/* ── Overview tab ──────────────────────── */}
            {activeTab === 'overview' && chartJSReady && (
              <div style={{
                display:             'grid',
                gridTemplateColumns: '1fr 1fr',
                gap:                 '12px',
              }}>
                <MonthlyRevenueChart data={monthlyRevenue} />
                <RevenueByPlatformChart data={revenueByPlatform} />
                <ROASChart data={revenueByPlatform} />
              </div>
            )}

            {/* ── Campaigns tab ─────────────────────── */}
            {activeTab === 'campaigns' && chartJSReady && (
              <div style={{
                display:             'grid',
                gridTemplateColumns: '1fr 1fr',
                gap:                 '12px',
              }}>
                <CTRByCampaignChart data={campaignData} />
                <FunnelChart data={funnelData} />
              </div>
            )}

            {/* ── Audience tab ──────────────────────── */}
            {activeTab === 'audience' && chartJSReady && (
              <div style={{
                display:             'grid',
                gridTemplateColumns: '1fr 1fr',
                gap:                 '12px',
              }}>
                <AudienceAgeChart data={audienceData} />
              </div>
            )}

            {/* ── Alerts tab ────────────────────────── */}
            {activeTab === 'alerts' && (
              <AlertsPanel alerts={alerts} />
            )}

            {/* Chart.js not ready yet */}
            {!chartJSReady && activeTab !== 'alerts' && (
              <div style={{
                textAlign:'center', padding:'40px',
                color:'#334155', fontFamily:'DM Mono, monospace', fontSize:'11px',
              }}>
                Loading chart library...
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}