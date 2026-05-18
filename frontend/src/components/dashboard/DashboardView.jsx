/**
 * DashboardView.jsx
 *
 * Main dashboard orchestrator. Renders:
 * - Top navigation bar (title, last refresh, refresh btn)
 * - Tab bar: Executive | Campaign | Platform | Audience | Alerts
 * - FilterBar: Platform pills + Year pills
 * - Active tab content
 * - Slide-in DrillDownPanel on any chart/KPI click
 *
 * All data comes from useDashboard().
 * All drill-down state managed by useDrillDown().
 * Chart.js loaded from CDN once on mount.
 *
 * Theme: matches your existing dark app exactly.
 * Background: #080d18 | Accent: #0ea5e9 | Font: Syne + DM Mono
 */

import { useEffect, useState } from 'react'
import { useDashboard }  from '../../hooks/useDashboard'
import { useDrillDown }  from '../../hooks/useDrillDown'
import FilterBar         from './shared/FilterBar'
import DrillDownPanel    from './panels/DrillDownPanel'
import AlertsPanel       from './panels/AlertsPanel'
import ExecutiveTab      from './tabs/ExecutiveTab'
import CampaignTab       from './tabs/CampaignTab'
import PlatformTab       from './tabs/PlatformTab'
import AudienceTab       from './tabs/AudienceTab'

// ── Load Chart.js from CDN once ───────────────────────────────
function useChartJS() {
  const [ready, setReady] = useState(!!window.Chart)
  useEffect(() => {
    if (window.Chart) { setReady(true); return }
    const script  = document.createElement('script')
    script.src    = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js'
    script.onload = () => setReady(true)
    script.onerror = () => console.error('[Dashboard] Chart.js failed to load from CDN')
    document.head.appendChild(script)
  }, [])
  return ready
}

// ── Tab bar ───────────────────────────────────────────────────
const TAB_CONFIG = [
  { id: 'executive', label: '▦ Executive',  title: 'Executive Summary',           subtitle: 'Overview of key performance metrics' },
  { id: 'campaign',  label: '◈ Campaigns',  title: 'Campaign Analytics',          subtitle: 'CTR, CPC, ROAS and conversion analysis' },
  { id: 'platform',  label: '⬡ Platforms',  title: 'Platform Comparison',         subtitle: 'Cross-platform performance benchmarking' },
  { id: 'audience',  label: '◉ Audience',   title: 'Audience Insights',           subtitle: 'Age, device, gender and sentiment analysis' },
  { id: 'alerts',    label: '⚡ Alerts',    title: 'Smart Alerts',               subtitle: 'AI-generated performance warnings' },
]

function TabBar({ active, onChange }) {
  return (
    <div style={{ display: 'flex', gap: '3px' }}>
      {TAB_CONFIG.map(t => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          style={{
            padding:      '7px 14px',
            borderRadius: '8px',
            border:       active === t.id
              ? '1px solid rgba(14,165,233,0.35)'
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
            whiteSpace:   'nowrap',
          }}
          onMouseEnter={e => {
            if (active !== t.id) {
              e.currentTarget.style.color      = '#94a3b8'
              e.currentTarget.style.background = 'rgba(255,255,255,0.03)'
            }
          }}
          onMouseLeave={e => {
            if (active !== t.id) {
              e.currentTarget.style.color      = '#475569'
              e.currentTarget.style.background = 'transparent'
            }
          }}
        >
          {t.label}
        </button>
      ))}
    </div>
  )
}

// ── Loading skeleton ──────────────────────────────────────────
function LoadingSkeleton() {
  return (
    <div>
      {/* KPI row skeleton */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '10px', marginBottom: '16px',
      }}>
        {[1, 2, 3, 4].map(i => (
          <div key={i} style={{
            height: '90px', borderRadius: '12px',
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.06)',
            animation: 'pulse 1.5s ease-in-out infinite',
          }} />
        ))}
      </div>
      {/* Chart rows skeleton */}
      {[[1, 1.6], [1.6, 1]].map((cols, ri) => (
        <div key={ri} style={{
          display: 'grid',
          gridTemplateColumns: cols.join('fr ') + 'fr',
          gap: '12px', marginBottom: '12px',
        }}>
          {cols.map((_, ci) => (
            <div key={ci} style={{
              height: '240px', borderRadius: '14px',
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.06)',
              animation: 'pulse 1.5s ease-in-out infinite',
            }} />
          ))}
        </div>
      ))}
    </div>
  )
}

// ── Error state ───────────────────────────────────────────────
function ErrorState({ error, onRetry }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      height: '60vh', gap: '16px',
    }}>
      <div style={{ fontSize: '36px', opacity: 0.3 }}>⚠</div>
      <div style={{
        color: '#f87171', fontFamily: 'DM Mono, monospace', fontSize: '12px',
        textAlign: 'center', maxWidth: '400px', lineHeight: 1.7,
      }}>
        {error || 'Failed to load dashboard data.'}
        <br />
        <span style={{ color: '#334155', fontSize: '11px' }}>
          Make sure your FastAPI backend is running on port 8000.
        </span>
      </div>
      <button
        onClick={onRetry}
        style={{
          padding: '8px 20px', borderRadius: '8px',
          background: 'rgba(14,165,233,0.1)',
          border: '1px solid rgba(14,165,233,0.25)',
          color: '#38bdf8', fontFamily: 'DM Mono, monospace',
          fontSize: '11px', cursor: 'pointer',
        }}
      >
        ↺ Try Again
      </button>
    </div>
  )
}

// ── Chart.js not ready yet ────────────────────────────────────
function ChartLoadingNote() {
  return (
    <div style={{
      textAlign: 'center', padding: '60px',
      color: '#1e3a5f', fontFamily: 'DM Mono, monospace', fontSize: '11px',
    }}>
      Loading chart library...
    </div>
  )
}

// ── Main DashboardView ────────────────────────────────────────
export default function DashboardView() {
  const chartJSReady = useChartJS()
  const { panel, openPanel, closePanel } = useDrillDown()

  const {
    activePlatform, activeYear, activeTab,
    isLoading, lastRefreshed, error,
    platforms, years,
    revenueByPlatform, monthlyRevenue, revenueByCategory,
    campaignData, campaignByObjective, influencerData,
    audienceAge, audienceDevice, audienceGender,
    funnelData, cacData, yoyData, refundData,
    platformBenchmark, platformRevenueShare, bestPlatformByCategory,
    sentimentData,
    alerts, forecast, kpis,
    setActiveTab, handleYearChange, handlePlatformChange, refresh,
  } = useDashboard()

  const activeTabConfig = TAB_CONFIG.find(t => t.id === activeTab) || TAB_CONFIG[0]

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

      {/* Grid texture */}
      <div style={{
        position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 0,
        backgroundImage: `
          linear-gradient(rgba(14,165,233,0.025) 1px, transparent 1px),
          linear-gradient(90deg, rgba(14,165,233,0.025) 1px, transparent 1px)
        `,
        backgroundSize: '48px 48px',
      }} />

      {/* ── Top Bar ─────────────────────────────────────── */}
      <div style={{
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        padding:        '12px 24px',
        borderBottom:   '1px solid rgba(255,255,255,0.055)',
        flexShrink:     0,
        zIndex:         2,
        backdropFilter: 'blur(8px)',
        background:     'rgba(5,10,18,0.7)',
      }}>
        {/* Title block */}
        <div>
          <div style={{
            fontSize: '14px', fontWeight: 700,
            color: '#f1f5f9', fontFamily: 'Syne, sans-serif',
          }}>
            {activeTabConfig.title}
          </div>
          <div style={{
            fontSize: '10px', color: '#334155',
            fontFamily: 'DM Mono, monospace', marginTop: '1px',
          }}>
            {activeTabConfig.subtitle}
          </div>
        </div>

        {/* Right controls */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {lastRefreshed && (
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '9px', color: '#1e3a5f', fontFamily: 'DM Mono, monospace' }}>
                Last Refresh
              </div>
              <div style={{ fontSize: '10px', color: '#334155', fontFamily: 'DM Mono, monospace' }}>
                {lastRefreshed.toLocaleDateString()} {lastRefreshed.toLocaleTimeString([], {
                  hour: '2-digit', minute: '2-digit',
                })}
              </div>
            </div>
          )}
          <button
            onClick={refresh}
            disabled={isLoading}
            title="Refresh all data"
            style={{
              padding: '6px 12px', borderRadius: '8px',
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.08)',
              color: isLoading ? '#1e3a5f' : '#475569',
              fontFamily: 'DM Mono, monospace', fontSize: '11px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s ease',
              display: 'flex', alignItems: 'center', gap: '5px',
            }}
            onMouseEnter={e => {
              if (!isLoading) {
                e.currentTarget.style.color       = '#94a3b8'
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.15)'
              }
            }}
            onMouseLeave={e => {
              e.currentTarget.style.color       = isLoading ? '#1e3a5f' : '#475569'
              e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'
            }}
          >
            <span style={{
              display: 'inline-block',
              animation: isLoading ? 'spin 1s linear infinite' : 'none',
            }}>
              ↺
            </span>
            {isLoading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* ── Tab Bar ─────────────────────────────────────── */}
      <div style={{
        padding:        '8px 24px',
        borderBottom:   '1px solid rgba(255,255,255,0.04)',
        flexShrink:     0,
        zIndex:         2,
        display:        'flex',
        alignItems:     'center',
        justifyContent: 'space-between',
        flexWrap:       'wrap',
        gap:            '8px',
        backdropFilter: 'blur(4px)',
        background:     'rgba(5,10,18,0.4)',
      }}>
        <TabBar active={activeTab} onChange={setActiveTab} />

        {/* Live indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <div style={{
            width: '5px', height: '5px', borderRadius: '50%',
            background: '#22c55e',
            boxShadow: '0 0 6px rgba(34,197,94,0.5)',
            animation: 'subtlePulse 2s ease-in-out infinite',
          }} />
          <span style={{
            fontSize: '9px', color: '#1e3a5f',
            fontFamily: 'DM Mono, monospace', letterSpacing: '0.06em',
          }}>
            LIVE · PostgreSQL
          </span>
        </div>
      </div>

      {/* ── Scrollable content area ──────────────────────── */}
      <div style={{
        flex:       1,
        overflowY:  'auto',
        padding:    '16px 24px 32px',
        zIndex:     1,
        scrollbarWidth: 'thin',
        scrollbarColor: '#0f2744 transparent',
      }}>

        {/* Error */}
        {error && <ErrorState error={error} onRetry={refresh} />}

        {/* Loading */}
        {!error && isLoading && <LoadingSkeleton />}

        {/* Content */}
        {!error && !isLoading && (
          <>
            {/* Filter bar — shown on all tabs except alerts */}
            {activeTab !== 'alerts' && (
              <FilterBar
                platforms={platforms}
                activePlatform={activePlatform}
                onPlatformChange={handlePlatformChange}
                years={years}
                activeYear={activeYear}
                onYearChange={handleYearChange}
              />
            )}

            {/* ── Executive Tab ─── */}
            {activeTab === 'executive' && (
              chartJSReady
                ? <ExecutiveTab
                    kpis={kpis}
                    revenueByPlatform={revenueByPlatform}
                    monthlyRevenue={monthlyRevenue}
                    revenueByCategory={revenueByCategory}
                    forecast={forecast}
                    openPanel={openPanel}
                    activePlatform={activePlatform}
                    activeYear={activeYear}
                  />
                : <ChartLoadingNote />
            )}

            {/* ── Campaign Tab ─── */}
            {activeTab === 'campaign' && (
              chartJSReady
                ? <CampaignTab
                    campaignData={campaignData}
                    campaignByObjective={campaignByObjective}
                    influencerData={influencerData}
                    funnelData={funnelData}
                    openPanel={openPanel}
                  />
                : <ChartLoadingNote />
            )}

            {/* ── Platform Tab ─── */}
            {activeTab === 'platform' && (
              chartJSReady
                ? <PlatformTab
                    platformBenchmark={platformBenchmark}
                    platformRevenueShare={platformRevenueShare}
                    bestPlatformByCategory={bestPlatformByCategory}
                    cacData={cacData}
                    yoyData={yoyData}
                    openPanel={openPanel}
                  />
                : <ChartLoadingNote />
            )}

            {/* ── Audience Tab ─── */}
            {activeTab === 'audience' && (
              chartJSReady
                ? <AudienceTab
                    audienceAge={audienceAge}
                    audienceDevice={audienceDevice}
                    audienceGender={audienceGender}
                    sentimentData={sentimentData}
                    refundData={refundData}
                    openPanel={openPanel}
                  />
                : <ChartLoadingNote />
            )}

            {/* ── Alerts Tab ─── */}
            {activeTab === 'alerts' && (
              <AlertsPanel alerts={alerts} />
            )}
          </>
        )}
      </div>

      {/* ── Drill-Down Panel (slide-in from right) ─── */}
      <DrillDownPanel panel={panel} onClose={closePanel} />

      {/* Spin keyframe for refresh icon */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}