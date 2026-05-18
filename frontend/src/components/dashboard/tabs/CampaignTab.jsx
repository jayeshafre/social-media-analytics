/**
 * tabs/CampaignTab.jsx
 *
 * Campaign Analytics — mirrors Page 2 of your Power BI dashboard:
 * - KPI row: Avg CTR, Avg CPC, Avg Conversion Rate, Total Conversions
 * - CTR by campaign type + platform (grouped bar)
 * - Top 10 campaigns by ROI (table)
 * - Conversion rate by objective (horizontal bar)
 * - Influencer vs Non-Influencer comparison
 * - Campaign stage (duration) performance
 * - All clickable → drill-down panel
 */

import { useEffect, useRef } from 'react'
import ChartCard from '../shared/ChartCard'
import KPICard from '../shared/KPICard'

const PLATFORM_COLORS = {
  Instagram:           '#e1306c',
  Facebook:            '#1877f2',
  YouTube:             '#ff4444',
  LinkedIn:            '#0a66c2',
  'WhatsApp Business': '#25d366',
  WhatsApp:            '#25d366',
}
function getColor(platform, i) {
  return PLATFORM_COLORS[platform] ||
    ['#0ea5e9','#8b5cf6','#22c55e','#f59e0b','#ef4444'][i % 5]
}

const fmt = {
  pct:  v => (parseFloat(v) * 100).toFixed(2) + '%',
  pct2: v => parseFloat(v).toFixed(2) + '%',
  curr: v => '₹' + parseFloat(v).toFixed(2),
  roas: v => parseFloat(v).toFixed(2) + 'x',
  num:  v => Number(Math.round(parseFloat(v))).toLocaleString('en-IN'),
  M:    v => (parseFloat(v) / 1e6).toFixed(2) + 'M',
}

// ── CTR by campaign type grouped bar ─────────────────────────
function CTRGroupedBarChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const campaignTypes = [...new Set(data.map(r => r.campaign_type))]
    const platforms     = [...new Set(data.map(r => r.platform))]

    const datasets = platforms.map((p, i) => {
      const color = getColor(p, i)
      return {
        label: p,
        data: campaignTypes.map(ct => {
          const row = data.find(r => r.platform === p && r.campaign_type === ct)
          return row ? parseFloat((parseFloat(row.avg_ctr) * 100).toFixed(3)) : 0
        }),
        backgroundColor: color,
        borderRadius: 4,
      }
    })

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: { labels: campaignTypes, datasets },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#475569', font: { size: 10 } }, grid: { display: false } },
          y: {
            ticks: { callback: v => v + '%', color: '#475569', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  const platforms = [...new Set(data?.map(r => r.platform) || [])]

  return (
    <>
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '8px' }}>
        {platforms.map((p, i) => (
          <span key={p} style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            fontSize: '10px', color: '#475569', fontFamily: 'DM Mono, monospace',
          }}>
            <span style={{
              width: '10px', height: '10px', borderRadius: '2px',
              background: getColor(p, i), display: 'inline-block',
            }} />
            {p}
          </span>
        ))}
      </div>
      <div style={{ position: 'relative', height: '200px' }}>
        <canvas ref={ref} role="img" aria-label="Avg CTR by campaign type and platform" />
      </div>
    </>
  )
}

// ── Conversion rate by objective ──────────────────────────────
function ObjectiveBarChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const sorted = [...data].sort((a, b) =>
      parseFloat(b.avg_conversion_rate) - parseFloat(a.avg_conversion_rate))
    const labels = sorted.map(r => r.campaign_objective)
    const values = sorted.map(r => parseFloat((parseFloat(r.avg_conversion_rate) * 100).toFixed(3)))

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: '#8b5cf6', borderRadius: 5 }],
      },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { callback: v => v + '%', color: '#475569', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
          y: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { display: false } },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  return (
    <div style={{ position: 'relative', height: '180px' }}>
      <canvas ref={ref} role="img" aria-label="Conversion rate by campaign objective" />
    </div>
  )
}

// ── Influencer comparison cards ───────────────────────────────
function InfluencerCompare({ data }) {
  if (!data?.length) return null
  const withInf    = data.find(r => r.influencer_used === true  || r.influencer_used === 't')
  const withoutInf = data.find(r => r.influencer_used === false || r.influencer_used === 'f')
  if (!withInf || !withoutInf) return null

  const cards = [
    { label: 'With Influencer',    data: withInf,    color: '#0ea5e9', bg: 'rgba(14,165,233,0.06)',  border: 'rgba(14,165,233,0.2)'  },
    { label: 'Without Influencer', data: withoutInf, color: '#475569', bg: 'rgba(255,255,255,0.03)', border: 'rgba(255,255,255,0.08)' },
  ]

  return (
    <div style={{ display: 'flex', gap: '10px' }}>
      {cards.map(({ label, data: d, color, bg, border }) => (
        <div key={label} style={{
          flex: 1, background: bg,
          border: `1px solid ${border}`,
          borderRadius: '10px', padding: '12px 14px',
        }}>
          <div style={{
            fontSize: '10px', color: '#475569',
            fontFamily: 'DM Mono, monospace', marginBottom: '8px',
          }}>
            {label}
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            {[
              { label: 'Avg ROAS', value: fmt.roas(d.avg_roas), color },
              { label: 'Avg CTR',  value: fmt.pct(d.avg_ctr),   color },
            ].map(stat => (
              <div key={stat.label}>
                <div style={{
                  fontSize: '16px', fontWeight: 700,
                  color: stat.color, fontFamily: 'Syne, sans-serif',
                }}>
                  {stat.value}
                </div>
                <div style={{
                  fontSize: '9px', color: '#475569',
                  fontFamily: 'DM Mono, monospace',
                }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Campaign Tab ──────────────────────────────────────────────
export default function CampaignTab({
  campaignData, campaignByObjective, influencerData,
  funnelData, openPanel,
}) {
  // Derive KPIs from campaign data
  const kpis = (() => {
    if (!campaignData?.length) return null
    const avgCTR  = campaignData.reduce((s, r) => s + (parseFloat(r.avg_ctr)  || 0), 0) / campaignData.length
    const avgCPC  = campaignData.reduce((s, r) => s + (parseFloat(r.avg_cpc)  || 0), 0) / campaignData.length
    const avgROAS = campaignData.reduce((s, r) => s + (parseFloat(r.avg_roas) || 0), 0) / campaignData.length
    return { avgCTR, avgCPC, avgROAS }
  })()

  const funnelKpi = funnelData?.reduce((a, b) =>
    (parseFloat(b.total_conversions) > parseFloat(a?.total_conversions || 0) ? b : a), null)
  const totalConversions = funnelData?.reduce((s, r) => s + (parseFloat(r.total_conversions) || 0), 0) || 0

  const handleCTRDrill = () => {
    if (!campaignData?.length) return
    openPanel({
      title:    'Campaign Performance by Type',
      subtitle: 'CTR, CPC, ROAS breakdown per campaign type per platform',
      rows:     campaignData,
      columns: [
        { key: 'platform',      label: 'Platform',  align: 'left' },
        { key: 'campaign_type', label: 'Type',      align: 'left' },
        { key: 'avg_ctr',       label: 'Avg CTR',   format: 'pct', mono: true, bar: true, barColor: '#0ea5e9' },
        { key: 'avg_cpc',       label: 'Avg CPC',   format: 'curr', mono: true },
        { key: 'avg_roas',      label: 'ROAS',      format: 'roas', mono: true },
        { key: 'total_campaigns',label: 'Count',    format: 'num',  mono: true },
      ],
    })
  }

  const handleObjectiveDrill = () => {
    if (!campaignByObjective?.length) return
    openPanel({
      title:    'Performance by Campaign Objective',
      subtitle: 'Conversion rate, CPC, ROAS by goal',
      rows:     campaignByObjective,
      columns: [
        { key: 'campaign_objective', label: 'Objective',    align: 'left' },
        { key: 'avg_conversion_rate',label: 'Conv Rate',    format: 'pct', bar: true, barColor: '#8b5cf6' },
        { key: 'avg_cpc',            label: 'Avg CPC',      format: 'curr', mono: true },
        { key: 'avg_roas',           label: 'ROAS',         format: 'roas', mono: true },
        { key: 'total_conversions',  label: 'Conversions',  format: 'num',  mono: true },
        { key: 'total_campaigns',    label: 'Campaigns',    format: 'num',  mono: true },
      ],
    })
  }

  const handleFunnelDrill = () => {
    if (!funnelData?.length) return
    openPanel({
      title:    'Conversion Funnel by Platform',
      subtitle: 'Impressions → Clicks → Conversions',
      highlight: [
        { label: 'Total Conversions', value: Number(totalConversions).toLocaleString('en-IN'), color: '#22c55e' },
      ],
      rows:     funnelData,
      columns: [
        { key: 'platform',               label: 'Platform',     align: 'left' },
        { key: 'total_impressions',      label: 'Impressions',  format: 'num',  mono: true },
        { key: 'total_clicks',           label: 'Clicks',       format: 'num',  mono: true },
        { key: 'total_conversions',      label: 'Conversions',  format: 'num',  mono: true, bar: true, barColor: '#22c55e' },
        { key: 'impression_to_click_pct',label: 'CTR%',         format: 'pct2', mono: true },
        { key: 'overall_funnel_pct',     label: 'Funnel%',      format: 'pct2', mono: true },
      ],
    })
  }

  return (
    <div>
      {/* KPI Row */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '10px', marginBottom: '16px',
      }}>
        <KPICard
          label="AVG CTR"
          value={kpis ? fmt.pct(kpis.avgCTR) : '—'}
          sub="vs 1.5% benchmark"
          subColor={kpis && kpis.avgCTR * 100 > 1.5 ? '#22c55e' : '#f87171'}
          icon="🖱" iconBg="rgba(14,165,233,0.12)"
          onClick={handleCTRDrill}
        />
        <KPICard
          label="AVG CPC"
          value={kpis ? fmt.curr(kpis.avgCPC) : '—'}
          sub="Cost per click"
          icon="₹" iconBg="rgba(245,158,11,0.12)"
          onClick={handleCTRDrill}
        />
        <KPICard
          label="AVG ROAS"
          value={kpis ? fmt.roas(kpis.avgROAS) : '—'}
          sub="Return on ad spend"
          icon="📊" iconBg="rgba(139,92,246,0.12)"
          onClick={handleCTRDrill}
        />
        <KPICard
          label="TOTAL CONVERSIONS"
          value={fmt.num(totalConversions)}
          sub="All campaigns"
          icon="✅" iconBg="rgba(34,197,94,0.12)"
          onClick={handleFunnelDrill}
        />
      </div>

      {/* Charts Row 1 */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1.4fr 1fr',
        gap: '12px', marginBottom: '12px',
      }}>
        <ChartCard
          title="Avg CTR by Campaign Type & Platform"
          subtitle="Click-through rate per ad format per channel"
          onClick={handleCTRDrill}
        >
          <CTRGroupedBarChart data={campaignData} />
        </ChartCard>

        <ChartCard
          title="Top 10 Campaigns by ROI"
          subtitle="Highest return on investment"
          onClick={handleCTRDrill}
        >
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '11px' }}>
              <thead>
                <tr>
                  {['Campaign', 'Platform', 'ROI', 'ROAS'].map(h => (
                    <th key={h} style={{
                      textAlign: 'left', padding: '4px 8px',
                      color: '#334155', fontFamily: 'DM Mono, monospace',
                      fontSize: '9px', textTransform: 'uppercase',
                      letterSpacing: '0.06em', borderBottom: '1px solid rgba(255,255,255,0.06)',
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(campaignData || []).slice(0, 8).map((row, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                    <td style={{ padding: '5px 8px', color: '#94a3b8', fontFamily: 'DM Mono, monospace', fontSize: '10px' }}>
                      {row.platform?.slice(0, 8)}·{row.campaign_type?.slice(0, 5)}
                    </td>
                    <td style={{ padding: '5px 8px', color: getColor(row.platform, i), fontSize: '10px', fontFamily: 'Syne, sans-serif' }}>
                      {row.platform}
                    </td>
                    <td style={{ padding: '5px 8px', color: '#4ade80', fontFamily: 'DM Mono, monospace', fontSize: '10px' }}>
                      {fmt.roas(row.avg_roi)}
                    </td>
                    <td style={{ padding: '5px 8px', color: '#94a3b8', fontFamily: 'DM Mono, monospace', fontSize: '10px' }}>
                      {fmt.roas(row.avg_roas)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ChartCard>
      </div>

      {/* Charts Row 2 */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
        gap: '12px',
      }}>
        <ChartCard
          title="Conversion Rate by Objective"
          subtitle="Goal → conversion efficiency"
          onClick={handleObjectiveDrill}
        >
          <ObjectiveBarChart data={campaignByObjective} />
        </ChartCard>

        <ChartCard
          title="Influencer vs Non-Influencer"
          subtitle="ROAS and CTR comparison"
        >
          <InfluencerCompare data={influencerData} />
        </ChartCard>

        <ChartCard
          title="Conversion Funnel"
          subtitle="Impressions → Clicks → Conversions"
          onClick={handleFunnelDrill}
        >
          {funnelData?.length > 0 && (
            <div>
              {[
                { label: 'Impressions', value: funnelData.reduce((s, r) => s + (parseFloat(r.total_impressions) || 0), 0), color: '#0ea5e9', width: '100%' },
                { label: 'Clicks',      value: funnelData.reduce((s, r) => s + (parseFloat(r.total_clicks)      || 0), 0), color: '#8b5cf6', width: '40%'  },
                { label: 'Conversions', value: funnelData.reduce((s, r) => s + (parseFloat(r.total_conversions) || 0), 0), color: '#22c55e', width: '15%'  },
              ].map(({ label, value, color, width }) => (
                <div key={label} style={{ marginBottom: '8px' }}>
                  <div style={{
                    background: `${color}22`,
                    border: `1px solid ${color}44`,
                    borderRadius: '6px', padding: '6px 12px',
                    width, minWidth: '120px',
                    fontSize: '11px', color, fontFamily: 'Syne, sans-serif', fontWeight: 600,
                  }}>
                    {label} — {Number(Math.round(value)).toLocaleString('en-IN')} total
                  </div>
                </div>
              ))}
              <div style={{
                fontSize: '10px', color: '#475569',
                fontFamily: 'DM Mono, monospace', marginTop: '8px',
              }}>
                CTR: {funnelData[0] ? (
                  (funnelData.reduce((s,r) => s + parseFloat(r.total_clicks||0),0) /
                  Math.max(1, funnelData.reduce((s,r) => s + parseFloat(r.total_impressions||0),0)) * 100).toFixed(2)
                ) : 0}%
              </div>
            </div>
          )}
        </ChartCard>
      </div>
    </div>
  )
}