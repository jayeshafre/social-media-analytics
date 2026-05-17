/**
 * DashboardCharts.jsx
 *
 * All chart rendering for the dashboard.
 * Uses Chart.js via CDN-loaded global (window.Chart).
 * Each chart is a self-contained component with useEffect.
 */

import { useEffect, useRef } from 'react'

const PLATFORM_COLORS = {
  Instagram:        '#e1306c',
  Facebook:         '#1877f2',
  YouTube:          '#ff4444',
  LinkedIn:         '#0a66c2',
  'WhatsApp Business': '#25d366',
  WhatsApp:         '#25d366',
}

function getColor(platform, index) {
  return PLATFORM_COLORS[platform] ||
    ['#0ea5e9','#8b5cf6','#22c55e','#f59e0b','#ef4444'][index % 5]
}

// ── Shared chart card wrapper ─────────────────────────────────
function ChartCard({ title, subtitle, children, fullWidth }) {
  return (
    <div style={{
      background:   'rgba(255,255,255,0.03)',
      border:       '1px solid rgba(255,255,255,0.07)',
      borderRadius: '14px',
      padding:      '16px 18px',
      gridColumn:   fullWidth ? '1 / -1' : undefined,
    }}>
      <div style={{
        fontSize:     '12px',
        fontWeight:   600,
        color:        '#cbd5e1',
        fontFamily:   'Syne, sans-serif',
        marginBottom: '2px',
      }}>{title}</div>
      <div style={{
        fontSize:     '10px',
        color:        '#334155',
        fontFamily:   'DM Mono, monospace',
        marginBottom: '12px',
      }}>{subtitle}</div>
      {children}
    </div>
  )
}

// ── Revenue by Platform — Horizontal Bar ─────────────────────
export function RevenueByPlatformChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const labels  = data.map(r => r.platform)
    const revenue = data.map(r => parseFloat((r.total_revenue / 1e6).toFixed(2)))
    const colors  = labels.map((l, i) => getColor(l, i))

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Revenue (₹M)',
          data:  revenue,
          backgroundColor: colors,
          borderRadius: 6,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: {
              callback: v => '₹' + v + 'M',
              color: '#475569',
              font: { size: 10 },
            },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
          y: {
            ticks: { color: '#64748b', font: { size: 10 } },
            grid: { display: false },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  return (
    <ChartCard title="Revenue by platform" subtitle="Total revenue per channel">
      <div style={{ position: 'relative', height: '190px' }}>
        <canvas ref={ref} role="img" aria-label="Revenue by platform horizontal bar chart" />
      </div>
    </ChartCard>
  )
}

// ── Monthly Revenue Trend — Line ──────────────────────────────
export function MonthlyRevenueChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const labels  = data.map(r => `${r.month_name?.slice(0,3)} ${r.year}`)
    const revenue = data.map(r => parseFloat((r.monthly_revenue / 1e6).toFixed(2)))
    const profit  = data.map(r => parseFloat((r.monthly_profit  / 1e6).toFixed(2)))

    chartRef.current = new window.Chart(ref.current, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Revenue',
            data:  revenue,
            borderColor: '#0ea5e9',
            backgroundColor: 'rgba(14,165,233,0.06)',
            tension: 0.4,
            fill: true,
            pointRadius: 2,
            borderWidth: 2,
          },
          {
            label: 'Profit',
            data:  profit,
            borderColor: '#22c55e',
            backgroundColor: 'rgba(34,197,94,0.06)',
            tension: 0.4,
            fill: true,
            pointRadius: 2,
            borderWidth: 2,
            borderDash: [4, 3],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: {
              color: '#475569',
              font: { size: 9 },
              maxTicksLimit: 12,
              maxRotation: 45,
            },
            grid: { color: 'rgba(255,255,255,0.04)' },
          },
          y: {
            ticks: {
              callback: v => '₹' + v + 'M',
              color: '#475569',
              font: { size: 10 },
            },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  return (
    <ChartCard title="Monthly revenue trend" subtitle="Revenue vs profit · all time" fullWidth>
      <div style={{ display: 'flex', gap: '16px', marginBottom: '8px' }}>
        {[
          { color: '#0ea5e9', label: 'Revenue' },
          { color: '#22c55e', label: 'Profit'  },
        ].map(({ color, label }) => (
          <span key={label} style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            fontSize: '10px', color: '#475569', fontFamily: 'DM Mono, monospace',
          }}>
            <span style={{
              width: '20px', height: '3px', background: color,
              borderRadius: '2px', display: 'inline-block',
            }} />
            {label}
          </span>
        ))}
      </div>
      <div style={{ position: 'relative', height: '170px' }}>
        <canvas ref={ref} role="img" aria-label="Monthly revenue and profit trend line chart" />
      </div>
    </ChartCard>
  )
}

// ── ROAS by Platform — Bar ────────────────────────────────────
export function ROASChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const labels = data.map(r => r.platform)
    const roas   = data.map(r => parseFloat(parseFloat(r.avg_roas).toFixed(2)))
    const colors = labels.map((l, i) => getColor(l, i))

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Avg ROAS',
          data: roas,
          backgroundColor: colors,
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { color: '#475569', font: { size: 10 } },
            grid: { display: false },
          },
          y: {
            ticks: {
              callback: v => v + 'x',
              color: '#475569',
              font: { size: 10 },
            },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  return (
    <ChartCard title="ROAS by platform" subtitle="Return on ad spend">
      <div style={{ position: 'relative', height: '190px' }}>
        <canvas ref={ref} role="img" aria-label="ROAS by platform bar chart" />
      </div>
    </ChartCard>
  )
}

// ── CTR by Campaign Type — Bar ────────────────────────────────
export function CTRByCampaignChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    // Group by campaign_type, average CTR
    const byType = {}
    data.forEach(r => {
      if (!byType[r.campaign_type]) byType[r.campaign_type] = []
      byType[r.campaign_type].push(parseFloat(r.avg_ctr || 0))
    })
    const labels = Object.keys(byType)
    const values = labels.map(t =>
      parseFloat((byType[t].reduce((a, b) => a + b, 0) / byType[t].length * 100).toFixed(3))
    )

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Avg CTR %',
          data: values,
          backgroundColor: '#0ea5e9',
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { color: '#475569', font: { size: 10 } },
            grid: { display: false },
          },
          y: {
            ticks: {
              callback: v => v + '%',
              color: '#475569',
              font: { size: 10 },
            },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  return (
    <ChartCard title="CTR by campaign type" subtitle="Click-through rate per ad format">
      <div style={{ position: 'relative', height: '200px' }}>
        <canvas ref={ref} role="img" aria-label="CTR by campaign type bar chart" />
      </div>
    </ChartCard>
  )
}

// ── Conversion Funnel — Horizontal Bar ────────────────────────
export function FunnelChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const labels = data.map(r => r.platform)
    const vals   = data.map(r => parseFloat(parseFloat(r.overall_funnel_pct || 0).toFixed(4)))
    const colors = labels.map((l, i) => getColor(l, i))

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Funnel %',
          data: vals,
          backgroundColor: colors,
          borderRadius: 6,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: {
              callback: v => v + '%',
              color: '#475569',
              font: { size: 10 },
            },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
          y: {
            ticks: { color: '#64748b', font: { size: 10 } },
            grid: { display: false },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  return (
    <ChartCard title="Conversion funnel" subtitle="Impression → click → conversion %">
      <div style={{ position: 'relative', height: '200px' }}>
        <canvas ref={ref} role="img" aria-label="Conversion funnel by platform" />
      </div>
    </ChartCard>
  )
}

// ── Audience Age Groups — Bar ─────────────────────────────────
export function AudienceAgeChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const sorted = [...data].sort((a, b) =>
      (a.audience_age_group || '').localeCompare(b.audience_age_group || '')
    )
    const labels = sorted.map(r => r.audience_age_group)
    const conv   = sorted.map(r =>
      parseFloat((parseFloat(r.avg_conversion_rate || 0) * 100).toFixed(3))
    )
    const roas   = sorted.map(r =>
      parseFloat(parseFloat(r.avg_roas || 0).toFixed(2))
    )

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Conv Rate %',
            data: conv,
            backgroundColor: '#f59e0b',
            borderRadius: 4,
            yAxisID: 'y',
          },
          {
            label: 'ROAS',
            data: roas,
            backgroundColor: '#8b5cf6',
            borderRadius: 4,
            yAxisID: 'y2',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { color: '#475569', font: { size: 10 } },
            grid: { display: false },
          },
          y: {
            position: 'left',
            ticks: {
              callback: v => v + '%',
              color: '#f59e0b',
              font: { size: 9 },
            },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
          y2: {
            position: 'right',
            ticks: {
              callback: v => v + 'x',
              color: '#8b5cf6',
              font: { size: 9 },
            },
            grid: { display: false },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  return (
    <ChartCard title="Audience by age group" subtitle="Conversion rate (amber) vs ROAS (purple)">
      <div style={{ display: 'flex', gap: '14px', marginBottom: '8px' }}>
        {[
          { color: '#f59e0b', label: 'Conv Rate' },
          { color: '#8b5cf6', label: 'ROAS'      },
        ].map(({ color, label }) => (
          <span key={label} style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            fontSize: '10px', color: '#475569', fontFamily: 'DM Mono, monospace',
          }}>
            <span style={{
              width: '10px', height: '10px', background: color,
              borderRadius: '2px', display: 'inline-block',
            }} />
            {label}
          </span>
        ))}
      </div>
      <div style={{ position: 'relative', height: '190px' }}>
        <canvas ref={ref} role="img" aria-label="Audience age group conversion rate and ROAS chart" />
      </div>
    </ChartCard>
  )
}