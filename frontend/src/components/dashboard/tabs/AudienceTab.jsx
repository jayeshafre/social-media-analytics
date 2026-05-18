/**
 * tabs/AudienceTab.jsx
 *
 * Audience Insights & Business Intelligence — mirrors Page 4:
 * - KPI row: Avg Conversion Rate, Top Age Group, Top Device, Avg Sentiment
 * - Conversion rate by age group (horizontal bar)
 * - Revenue by device type (donut)
 * - Gender targeting performance (matrix table)
 * - Sentiment score by platform (bar)
 * - Avg ROAS by age group (bar)
 * - Refund status breakdown (donut)
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
function getColor(p, i) {
  return PLATFORM_COLORS[p] || ['#0ea5e9','#8b5cf6','#22c55e','#f59e0b','#ef4444'][i % 5]
}

const DEVICE_COLORS  = { Mobile: '#8b5cf6', Desktop: '#0ea5e9', Tablet: '#f59e0b' }
const REFUND_COLORS  = { 'No Refund': '#22c55e', Refunded: '#ef4444', Partial: '#f59e0b' }

const fmt = {
  pct:  v => (parseFloat(v) * 100).toFixed(2) + '%',
  pct2: v => parseFloat(v).toFixed(2) + '%',
  roas: v => parseFloat(v).toFixed(2) + 'x',
  num:  v => Number(Math.round(parseFloat(v))).toLocaleString('en-IN'),
  curr: v => '₹' + parseFloat(v).toFixed(2),
}

// ── Age Group Conversion Rate ─────────────────────────────────
function AgeConversionChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const sorted = [...data].sort((a, b) =>
      parseFloat(b.avg_conversion_rate) - parseFloat(a.avg_conversion_rate))
    const labels = sorted.map(r => r.audience_age_group)
    const values = sorted.map(r =>
      parseFloat((parseFloat(r.avg_conversion_rate) * 100).toFixed(3)))

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: '#22c55e',
          borderRadius: 5,
        }],
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
    <div style={{ position: 'relative', height: '170px' }}>
      <canvas ref={ref} role="img" aria-label="Conversion rate by age group" />
    </div>
  )
}

// ── Revenue by Device Donut ───────────────────────────────────
function DeviceDonutChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const labels = data.map(r => r.device_type)
    const values = data.map(r => parseFloat(r.total_conversions) || 0)
    const colors = labels.map(l => DEVICE_COLORS[l] || '#475569')

    chartRef.current = new window.Chart(ref.current, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderColor: '#080d18',
          borderWidth: 3,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.label}: ${ctx.raw.toLocaleString('en-IN')} conversions`,
            },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  if (!data?.length) return null

  const total = data.reduce((s, r) => s + (parseFloat(r.total_conversions) || 0), 0)

  return (
    <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
      <div style={{ position: 'relative', width: '130px', height: '130px', flexShrink: 0 }}>
        <canvas ref={ref} role="img" aria-label="Revenue by device type donut" />
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%,-50%)', textAlign: 'center', pointerEvents: 'none',
        }}>
          <div style={{ fontSize: '10px', color: '#334155', fontFamily: 'DM Mono, monospace' }}>
            Total
          </div>
          <div style={{ fontSize: '13px', fontWeight: 700, color: '#f1f5f9', fontFamily: 'Syne, sans-serif' }}>
            {fmt.num(total)}
          </div>
        </div>
      </div>
      <ul style={{ listStyle: 'none', flex: 1 }}>
        {data.map(r => {
          const pct = total > 0 ? ((parseFloat(r.total_conversions) / total) * 100).toFixed(1) : 0
          const color = DEVICE_COLORS[r.device_type] || '#475569'
          return (
            <li key={r.device_type} style={{
              display: 'flex', alignItems: 'center', gap: '7px',
              padding: '3px 0', fontSize: '11px',
            }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: color, flexShrink: 0 }} />
              <span style={{ color: '#94a3b8', fontFamily: 'Syne, sans-serif', flex: 1 }}>
                {r.device_type}
              </span>
              <span style={{ color: '#64748b', fontFamily: 'DM Mono, monospace', fontSize: '10px' }}>
                {pct}%
              </span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

// ── Sentiment by Platform bar ─────────────────────────────────
function SentimentChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const sorted = [...data].sort((a, b) =>
      parseFloat(b.avg_sentiment) - parseFloat(a.avg_sentiment))
    const labels = sorted.map(r => r.platform)
    const values = sorted.map(r => parseFloat(parseFloat(r.avg_sentiment).toFixed(3)))
    const colors = labels.map((l, i) => getColor(l, i))

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderRadius: 5,
        }],
      },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            min: 0.68,
            ticks: { color: '#475569', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
          y: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { display: false } },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  return (
    <div style={{ position: 'relative', height: '160px' }}>
      <canvas ref={ref} role="img" aria-label="Avg sentiment score by platform" />
    </div>
  )
}

// ── ROAS by Age Group bar ─────────────────────────────────────
function ROASByAgeChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const sorted = [...data].sort((a, b) =>
      parseFloat(b.avg_roas) - parseFloat(a.avg_roas))
    const labels = sorted.map(r => r.audience_age_group)
    const values = sorted.map(r => parseFloat(parseFloat(r.avg_roas).toFixed(2)))

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: '#8b5cf6',
          borderRadius: 5,
        }],
      },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { callback: v => v + 'x', color: '#475569', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
          y: { ticks: { color: '#64748b', font: { size: 10 } }, grid: { display: false } },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  return (
    <div style={{ position: 'relative', height: '160px' }}>
      <canvas ref={ref} role="img" aria-label="Avg ROAS by age group" />
    </div>
  )
}

// ── Refund Donut ──────────────────────────────────────────────
function RefundDonutChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const labels = data.map(r => r.refund_status)
    const values = data.map(r => parseFloat(r.total_conversions) || 0)
    const colors = labels.map(l => REFUND_COLORS[l] || '#475569')

    chartRef.current = new window.Chart(ref.current, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderColor: '#080d18',
          borderWidth: 3,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.label}: ${ctx.parsed.toFixed(1)}%`,
            },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  if (!data?.length) return null

  return (
    <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
      <div style={{ position: 'relative', width: '110px', height: '110px', flexShrink: 0 }}>
        <canvas ref={ref} role="img" aria-label="Refund status breakdown donut" />
      </div>
      <ul style={{ listStyle: 'none', flex: 1 }}>
        {data.map(r => {
          const color = REFUND_COLORS[r.refund_status] || '#475569'
          return (
            <li key={r.refund_status} style={{
              display: 'flex', alignItems: 'center', gap: '7px',
              padding: '3px 0', fontSize: '11px',
            }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: color, flexShrink: 0 }} />
              <span style={{ color: '#94a3b8', fontFamily: 'Syne, sans-serif', flex: 1 }}>
                {r.refund_status}
              </span>
              <span style={{ color, fontFamily: 'DM Mono, monospace', fontSize: '10px', fontWeight: 600 }}>
                {parseFloat(r.pct_of_total).toFixed(1)}%
              </span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

// ── Gender Matrix Table ───────────────────────────────────────
function GenderMatrix({ data }) {
  if (!data?.length) return null

  const maxROAS = Math.max(...data.map(r => parseFloat(r.avg_roas) || 0))

  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '11px' }}>
      <thead>
        <tr>
          {['Gender', 'Avg ROAS', 'Avg CTR', 'Revenue'].map(h => (
            <th key={h} style={{
              textAlign: h === 'Gender' ? 'left' : 'right',
              padding: '5px 8px', color: '#334155',
              fontFamily: 'DM Mono, monospace', fontSize: '9px',
              textTransform: 'uppercase', letterSpacing: '0.06em',
              borderBottom: '1px solid rgba(255,255,255,0.07)',
            }}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => {
          const isTopROAS = parseFloat(row.avg_roas) === maxROAS
          return (
            <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
              <td style={{ padding: '6px 8px', color: '#94a3b8', fontFamily: 'Syne, sans-serif', fontWeight: 600 }}>
                {row.audience_gender}
              </td>
              <td style={{
                padding: '6px 8px', textAlign: 'right',
                fontFamily: 'DM Mono, monospace',
                color: isTopROAS ? '#4ade80' : '#64748b',
                fontWeight: isTopROAS ? 700 : 400,
              }}>
                {fmt.roas(row.avg_roas)}
              </td>
              <td style={{ padding: '6px 8px', textAlign: 'right', fontFamily: 'DM Mono, monospace', color: '#64748b' }}>
                {(parseFloat(row.avg_ctr) * 100).toFixed(2)}%
              </td>
              <td style={{ padding: '6px 8px', textAlign: 'right', fontFamily: 'DM Mono, monospace', color: '#64748b' }}>
                ₹{(parseFloat(row.total_revenue) / 1e6).toFixed(1)}M
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}

// ── Audience Tab ──────────────────────────────────────────────
export default function AudienceTab({
  audienceAge, audienceDevice, audienceGender,
  sentimentData, refundData, openPanel,
}) {
  // Derive KPIs
  const topAge = audienceAge?.reduce((a, b) =>
    parseFloat(b.avg_conversion_rate) > parseFloat(a?.avg_conversion_rate || 0) ? b : a, null)
  const topDevice = audienceDevice?.reduce((a, b) =>
    parseFloat(b.total_conversions) > parseFloat(a?.total_conversions || 0) ? b : a, null)
  const avgConvRate = audienceAge?.length
    ? audienceAge.reduce((s, r) => s + (parseFloat(r.avg_conversion_rate) || 0), 0) / audienceAge.length
    : 0
  const avgSentiment = sentimentData?.length
    ? sentimentData.reduce((s, r) => s + (parseFloat(r.avg_sentiment) || 0), 0) / sentimentData.length
    : 0

  const handleAgeDrill = () => {
    if (!audienceAge?.length) return
    openPanel({
      title:    'Audience Performance by Age Group',
      subtitle: 'Conversion rate, CTR, ROAS per age segment',
      rows:     audienceAge,
      columns: [
        { key: 'audience_age_group',  label: 'Age Group',   align: 'left' },
        { key: 'avg_conversion_rate', label: 'Conv Rate',   format: 'pct', bar: true, barColor: '#22c55e' },
        { key: 'avg_ctr',             label: 'Avg CTR',     format: 'pct', mono: true },
        { key: 'avg_roas',            label: 'Avg ROAS',    format: 'roas', mono: true },
        { key: 'total_campaigns',     label: 'Campaigns',   format: 'num',  mono: true },
        { key: 'total_conversions',   label: 'Conversions', format: 'num',  mono: true },
      ],
    })
  }

  const handleDeviceDrill = () => {
    if (!audienceDevice?.length) return
    openPanel({
      title:    'Performance by Device Type',
      subtitle: 'Mobile vs Desktop vs Tablet',
      rows:     audienceDevice,
      columns: [
        { key: 'device_type',         label: 'Device',      align: 'left' },
        { key: 'avg_conversion_rate', label: 'Conv Rate',   format: 'pct', bar: true, barColor: '#8b5cf6' },
        { key: 'avg_ctr',             label: 'Avg CTR',     format: 'pct',  mono: true },
        { key: 'avg_roas',            label: 'Avg ROAS',    format: 'roas', mono: true },
        { key: 'total_conversions',   label: 'Conversions', format: 'num',  mono: true },
        { key: 'total_campaigns',     label: 'Campaigns',   format: 'num',  mono: true },
      ],
    })
  }

  const handleGenderDrill = () => {
    if (!audienceGender?.length) return
    openPanel({
      title:    'Gender Targeting Performance',
      subtitle: 'ROAS, CTR, and revenue by audience gender',
      rows:     audienceGender,
      columns: [
        { key: 'audience_gender',     label: 'Gender',      align: 'left' },
        { key: 'avg_roas',            label: 'Avg ROAS',    format: 'roas', bar: true, barColor: '#0ea5e9' },
        { key: 'avg_ctr',             label: 'Avg CTR',     format: 'pct',  mono: true },
        { key: 'avg_conversion_rate', label: 'Conv Rate',   format: 'pct',  mono: true },
        { key: 'total_revenue',       label: 'Revenue',     format: 'currency' },
        { key: 'total_campaigns',     label: 'Campaigns',   format: 'num',  mono: true },
      ],
    })
  }

  const handleSentimentDrill = () => {
    if (!sentimentData?.length) return
    openPanel({
      title:    'Sentiment Score by Platform',
      subtitle: '0 = negative · 1 = positive',
      rows:     sentimentData,
      columns: [
        { key: 'platform',            label: 'Platform',       align: 'left' },
        { key: 'avg_sentiment',       label: 'Avg Sentiment',  bar: true, barColor: '#f59e0b' },
        { key: 'min_sentiment',       label: 'Min',            mono: true },
        { key: 'max_sentiment',       label: 'Max',            mono: true },
        { key: 'avg_engagement_rate', label: 'Engagement',     format: 'pct', mono: true },
        { key: 'total_snapshots',     label: 'Snapshots',      format: 'num', mono: true },
      ],
      note: 'Sentiment score ranges from 0 (very negative) to 1 (very positive). Scores above 0.7 are considered positive.',
    })
  }

  const handleRefundDrill = () => {
    if (!refundData?.length) return
    openPanel({
      title:    'Refund Status Breakdown',
      subtitle: 'Conversion revenue impact by refund status',
      rows:     refundData,
      columns: [
        { key: 'refund_status',       label: 'Status',      align: 'left' },
        { key: 'total_conversions',   label: 'Count',       format: 'num',      bar: true, barColor: '#22c55e' },
        { key: 'pct_of_total',        label: '% of Total',  format: 'pct2',     mono: true },
        { key: 'gross_revenue',       label: 'Revenue',     format: 'currency' },
        { key: 'gross_profit',        label: 'Profit',      format: 'currency' },
        { key: 'avg_order_value',     label: 'Avg Order',   format: 'currency' },
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
          label="AVG CONVERSION RATE"
          value={fmt.pct(avgConvRate)}
          sub="Across all campaigns"
          icon="🔄" iconBg="rgba(34,197,94,0.12)"
          onClick={handleAgeDrill}
        />
        <KPICard
          label="TOP CONVERTING AGE"
          value={topAge?.audience_age_group || '—'}
          sub={topAge ? 'Highest conv rate' : ''}
          subColor="#22c55e"
          icon="👥" iconBg="rgba(14,165,233,0.12)"
          onClick={handleAgeDrill}
        />
        <KPICard
          label="TOP DEVICE"
          value={topDevice?.device_type || '—'}
          sub={topDevice
            ? ((parseFloat(topDevice.total_conversions) /
               Math.max(1, audienceDevice?.reduce((s, r) => s + parseFloat(r.total_conversions || 0), 0)) * 100).toFixed(1)) + '% of conversions'
            : ''}
          subColor="#8b5cf6"
          icon="📱" iconBg="rgba(139,92,246,0.12)"
          onClick={handleDeviceDrill}
        />
        <KPICard
          label="AVG SENTIMENT SCORE"
          value={avgSentiment.toFixed(3)}
          sub="0 = negative · 1 = positive"
          subColor={avgSentiment > 0.7 ? '#22c55e' : '#f59e0b'}
          icon="💬" iconBg="rgba(245,158,11,0.12)"
          onClick={handleSentimentDrill}
        />
      </div>

      {/* Row 1: Age Conv + Device Donut + Gender Matrix */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
        gap: '12px', marginBottom: '12px',
      }}>
        <ChartCard
          title="Conv Rate by Age Group"
          subtitle="Conversion rate per audience age segment"
          onClick={handleAgeDrill}
        >
          <AgeConversionChart data={audienceAge} />
        </ChartCard>

        <ChartCard
          title="Revenue by Device Type"
          subtitle="Mobile vs Desktop vs Tablet"
          onClick={handleDeviceDrill}
        >
          <DeviceDonutChart data={audienceDevice} />
        </ChartCard>

        <ChartCard
          title="Gender Targeting Performance"
          subtitle="ROAS, CTR and revenue by gender"
          onClick={handleGenderDrill}
        >
          <GenderMatrix data={audienceGender} />
        </ChartCard>
      </div>

      {/* Row 2: Sentiment + ROAS by Age + Refund */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
        gap: '12px',
      }}>
        <ChartCard
          title="Sentiment Score by Platform"
          subtitle="Audience reaction score · 0–1 scale"
          onClick={handleSentimentDrill}
        >
          <SentimentChart data={sentimentData} />
        </ChartCard>

        <ChartCard
          title="Avg ROAS by Age Group"
          subtitle="Return on ad spend per age segment"
          onClick={handleAgeDrill}
        >
          <ROASByAgeChart data={audienceAge} />
        </ChartCard>

        <ChartCard
          title="Refund Status Breakdown"
          subtitle="No Refund vs Refunded vs Partial"
          onClick={handleRefundDrill}
        >
          <RefundDonutChart data={refundData} />
        </ChartCard>
      </div>
    </div>
  )
}