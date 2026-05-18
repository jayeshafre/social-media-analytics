/**
 * tabs/ExecutiveTab.jsx
 *
 * Executive Summary — mirrors Page 1 of your Power BI dashboard:
 * - 4 KPI cards (Revenue, Profit, ROAS, Campaigns) with sparklines
 * - Total Revenue by Platform (donut chart)
 * - Total Revenue by Month (area line chart)
 * - Revenue by Business Category (horizontal bar)
 * - Key Insights sidebar panel
 * - Every card/chart is clickable → drill-down panel
 */

import { useEffect, useRef } from 'react'
import ChartCard from '../shared/ChartCard'
import KPICard from '../shared/KPICard'

const PLATFORM_COLORS = {
  YouTube:              '#ff4444',
  Facebook:             '#1877f2',
  Instagram:            '#e1306c',
  LinkedIn:             '#0a66c2',
  'WhatsApp Business':  '#25d366',
  WhatsApp:             '#25d366',
}

function getColor(platform, index) {
  return PLATFORM_COLORS[platform] ||
    ['#0ea5e9','#8b5cf6','#22c55e','#f59e0b','#ef4444'][index % 5]
}

const fmt = {
  currency: v => {
    const n = parseFloat(v) || 0
    return n >= 1e9
      ? '₹' + (n / 1e9).toFixed(2) + 'bn'
      : n >= 1e7
        ? '₹' + (n / 1e7).toFixed(2) + 'Cr'
        : '₹' + (n / 1e6).toFixed(1) + 'M'
  },
  roas:  v => parseFloat(v).toFixed(2) + 'x',
  count: v => {
    const n = parseFloat(v) || 0
    return n >= 1000 ? (n / 1000).toFixed(0) + 'K' : Math.round(n).toString()
  },
}

// ── Donut Chart ───────────────────────────────────────────────
function DonutChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const labels  = data.map(r => r.platform)
    const values  = data.map(r => parseFloat(r.total_revenue) || 0)
    const colors  = labels.map((l, i) => getColor(l, i))

    chartRef.current = new window.Chart(ref.current, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderColor: '#080d18',
          borderWidth: 3,
          hoverBorderWidth: 4,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.label}: ${fmt.currency(ctx.raw)} (${ctx.parsed.toFixed(1)}%)`,
            },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [data])

  if (!data?.length) return null

  const total = data.reduce((s, r) => s + (parseFloat(r.total_revenue) || 0), 0)

  return (
    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
      <div style={{ position: 'relative', width: '160px', height: '160px', flexShrink: 0 }}>
        <canvas
          ref={ref}
          role="img"
          aria-label="Revenue by platform donut chart"
        />
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%,-50%)', textAlign: 'center',
          pointerEvents: 'none',
        }}>
          <div style={{
            fontSize: '15px', fontWeight: 700,
            color: '#f1f5f9', fontFamily: 'Syne, sans-serif', lineHeight: 1.2,
          }}>
            {fmt.currency(total)}
          </div>
          <div style={{
            fontSize: '9px', color: '#334155',
            fontFamily: 'DM Mono, monospace', marginTop: '2px',
          }}>
            Total
          </div>
        </div>
      </div>

      <ul style={{ listStyle: 'none', flex: 1 }}>
        {data.map((r, i) => {
          const pct = total > 0 ? ((parseFloat(r.total_revenue) / total) * 100).toFixed(1) : 0
          return (
            <li key={r.platform} style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              padding: '3px 0',
            }}>
              <span style={{
                width: '8px', height: '8px', borderRadius: '50%',
                background: getColor(r.platform, i), flexShrink: 0,
              }} />
              <span style={{
                fontSize: '11px', color: '#94a3b8',
                fontFamily: 'Syne, sans-serif', flex: 1,
              }}>
                {r.platform}
              </span>
              <span style={{
                fontSize: '10px', color: '#64748b',
                fontFamily: 'DM Mono, monospace',
              }}>
                {fmt.currency(r.total_revenue)} ({pct}%)
              </span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}

// ── Monthly Revenue Area Line ─────────────────────────────────
function MonthlyAreaChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  // Stable cache key — forces chart destroy+recreate when platform/year changes
  const dataKey = data?.map(r => `${r.year}-${r.month}-${r.monthly_revenue}`).join('|') || ''

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) { chartRef.current.destroy(); chartRef.current = null }

    const labels  = data.map(r => r.month_name?.slice(0, 3) || '')
    const revenue = data.map(r => parseFloat((parseFloat(r.monthly_revenue) / 1e6).toFixed(2)))
    const profit  = data.map(r => parseFloat((parseFloat(r.monthly_profit)  / 1e6).toFixed(2)))

    chartRef.current = new window.Chart(ref.current, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Revenue (₹M)',
            data: revenue,
            borderColor: '#0ea5e9',
            backgroundColor: 'rgba(14,165,233,0.08)',
            tension: 0.4, fill: true,
            pointRadius: 3, pointBackgroundColor: '#0ea5e9',
            borderWidth: 2,
          },
          {
            label: 'Profit (₹M)',
            data: profit,
            borderColor: '#22c55e',
            backgroundColor: 'rgba(34,197,94,0.05)',
            tension: 0.4, fill: true,
            pointRadius: 3, pointBackgroundColor: '#22c55e',
            borderWidth: 2,
            borderDash: [5, 3],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: { label: ctx => ` ${ctx.dataset.label}: ₹${ctx.raw}M` },
          },
        },
        scales: {
          x: {
            ticks: {
              color: '#475569', font: { size: 10 },
              autoSkip: false, maxRotation: 0,
            },
            grid: { color: 'rgba(255,255,255,0.04)' },
          },
          y: {
            ticks: { callback: v => '₹' + v + 'M', color: '#475569', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
        },
      },
    })
    return () => chartRef.current?.destroy()
  }, [dataKey])

  return (
    <>
      <div style={{ display: 'flex', gap: '16px', marginBottom: '8px' }}>
        {[{ color: '#0ea5e9', label: 'Revenue' }, { color: '#22c55e', label: 'Profit' }].map(({ color, label }) => (
          <span key={label} style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            fontSize: '10px', color: '#475569', fontFamily: 'DM Mono, monospace',
          }}>
            <span style={{ width: '18px', height: '3px', background: color, borderRadius: '2px', display: 'inline-block' }} />
            {label}
          </span>
        ))}
      </div>
      <div style={{ position: 'relative', height: '170px' }}>
        <canvas ref={ref} role="img" aria-label="Monthly revenue and profit area chart" />
      </div>
    </>
  )
}

// ── Category Horizontal Bar ───────────────────────────────────
function CategoryBarChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  const dataKey = data?.map(r => `${r.business_category}-${r.total_revenue}`).join('|') || ''

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) { chartRef.current.destroy(); chartRef.current = null }

    const sorted = [...data].sort((a, b) => parseFloat(b.total_revenue) - parseFloat(a.total_revenue))
    const top10  = sorted.slice(0, 10)
    const labels = top10.map(r => r.business_category)
    const values = top10.map(r => parseFloat((parseFloat(r.total_revenue) / 1e6).toFixed(2)))
    const colors = [
      '#0ea5e9','#8b5cf6','#22c55e','#f59e0b','#ef4444',
      '#06b6d4','#a78bfa','#4ade80','#fbbf24','#f87171',
    ]

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: colors.slice(0, labels.length),
          borderRadius: 5,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { callback: v => '₹' + v + 'M', color: '#475569', font: { size: 10 } },
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
  }, [dataKey])

  return (
    <div style={{ position: 'relative', height: `${Math.max(200, (data?.length || 5) * 28)}px` }}>
      <canvas ref={ref} role="img" aria-label="Revenue by business category bar chart" />
    </div>
  )
}

// ── Key Insights Panel ────────────────────────────────────────
function KeyInsights({ revenueByPlatform, monthlyRevenue, revenueByCategory }) {
  if (!revenueByPlatform?.length) return null

  const totalRevenue = revenueByPlatform.reduce((s, r) => s + (parseFloat(r.total_revenue) || 0), 0)
  const topPlatform  = revenueByPlatform[0]
  const peakMonth    = monthlyRevenue?.reduce((a, b) =>
    (parseFloat(b.monthly_revenue) > parseFloat(a?.monthly_revenue || 0) ? b : a), null)
  const topCategory  = revenueByCategory?.[0]

  const insights = [
    {
      icon: '▲', color: '#22c55e', bg: 'rgba(34,197,94,0.12)',
      title: 'Total Revenue',
      text: `Total revenue is ${fmt.currency(totalRevenue)} across all platforms.`,
    },
    {
      icon: '★', color: '#0ea5e9', bg: 'rgba(14,165,233,0.12)',
      title: 'Top Platform',
      text: `${topPlatform?.platform} generates the highest revenue at ${fmt.currency(topPlatform?.total_revenue)} (${
        totalRevenue > 0
          ? ((parseFloat(topPlatform?.total_revenue) / totalRevenue) * 100).toFixed(1)
          : 0
      }%).`,
    },
    ...(peakMonth ? [{
      icon: '◈', color: '#f59e0b', bg: 'rgba(245,158,11,0.12)',
      title: 'Peak Month',
      text: `${peakMonth.month_name} ${peakMonth.year} has the highest revenue at ${fmt.currency(peakMonth.monthly_revenue)}.`,
    }] : []),
    ...(topCategory ? [{
      icon: '◉', color: '#a78bfa', bg: 'rgba(167,139,250,0.12)',
      title: 'Top Category',
      text: `${topCategory.business_category} leads with ${fmt.currency(topCategory.total_revenue)} in revenue.`,
    }] : []),
  ]

  return (
    <div style={{
      background: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(255,255,255,0.07)',
      borderRadius: '14px', padding: '16px 18px',
    }}>
      <div style={{
        fontSize: '12px', fontWeight: 600,
        color: '#cbd5e1', fontFamily: 'Syne, sans-serif', marginBottom: '12px',
      }}>
        Key Insights
      </div>
      {insights.map((ins, i) => (
        <div key={i} style={{
          display: 'flex', gap: '10px', alignItems: 'flex-start',
          padding: '8px 0',
          borderBottom: i < insights.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none',
        }}>
          <div style={{
            width: '28px', height: '28px', borderRadius: '50%',
            background: ins.bg, display: 'flex',
            alignItems: 'center', justifyContent: 'center',
            fontSize: '12px', color: ins.color, flexShrink: 0,
          }}>
            {ins.icon}
          </div>
          <div>
            <div style={{
              fontSize: '11px', fontWeight: 600,
              color: ins.color, fontFamily: 'Syne, sans-serif', marginBottom: '2px',
            }}>
              {ins.title}
            </div>
            <div style={{
              fontSize: '11px', color: '#64748b',
              fontFamily: 'DM Mono, monospace', lineHeight: 1.5,
            }}>
              {ins.text}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Executive Tab ─────────────────────────────────────────────
export default function ExecutiveTab({
  kpis, revenueByPlatform, monthlyRevenue, revenueByCategory,
  forecast, openPanel, activePlatform = 'All', activeYear = 'All',
  monthlyRevenueForChart, revenueByCategoryForChart,
}) {
  // ── Client-side filtering ─────────────────────────────────
  // Donut: when a specific platform is selected, show only that platform in the donut
  // When 'All', show all platforms with their full revenue
  const filteredPlatformData = activePlatform === 'All'
    ? revenueByPlatform
    : revenueByPlatform?.filter(r => r.platform === activePlatform)

  // Sparklines follow the filtered monthly data (already year-filtered by hook)
  const revenueSparkData = monthlyRevenue?.slice(-12).map(r => parseFloat(r.monthly_revenue) || 0)
  const profitSparkData  = monthlyRevenue?.slice(-12).map(r => parseFloat(r.monthly_profit)  || 0)

  const handlePlatformDrill = () => {
    if (!revenueByPlatform?.length) return
    openPanel({
      title:    'Revenue by Platform — Full Breakdown',
      subtitle: 'All platforms · sorted by total revenue',
      highlight: [
        { label: 'Total Revenue', value: fmt.currency(kpis?.totalRevenue), color: '#0ea5e9' },
        { label: 'Avg ROAS',      value: fmt.roas(kpis?.avgROAS),          color: '#22c55e' },
        { label: 'Total Spend',   value: fmt.currency(kpis?.totalSpend),   color: '#f59e0b' },
      ],
      rows: revenueByPlatform,
      columns: [
        { key: 'platform',       label: 'Platform',    align: 'left'  },
        { key: 'total_revenue',  label: 'Revenue',     format: 'currency', bar: true, barColor: '#0ea5e9' },
        { key: 'total_profit',   label: 'Profit',      format: 'currency' },
        { key: 'avg_roas',       label: 'ROAS',        format: 'roas',    mono: true },
        { key: 'total_campaigns',label: 'Campaigns',   format: 'num',     mono: true },
      ],
      note: 'Revenue = total revenue generated from all campaigns on each platform.',
    })
  }

  const handleCategoryDrill = () => {
    const catData = revenueByCategoryForChart || revenueByCategory
    if (!catData?.length) return
    openPanel({
      title:    'Revenue by Business Category',
      subtitle: activePlatform !== 'All' ? `${activePlatform} · ${activeYear !== 'All' ? activeYear : 'All years'}` : 'All categories · sorted by total profit',
      rows: catData,
      columns: [
        { key: 'business_category', label: 'Category',   align: 'left' },
        { key: 'total_revenue',     label: 'Revenue',    format: 'currency', bar: true, barColor: '#8b5cf6' },
        { key: 'total_profit',      label: 'Profit',     format: 'currency' },
        { key: 'avg_roi',           label: 'Avg ROI',    format: 'pct',     mono: true },
        { key: 'avg_roas',          label: 'Avg ROAS',   format: 'roas',    mono: true },
        { key: 'total_campaigns',   label: 'Campaigns',  format: 'num',     mono: true },
      ],
    })
  }

  const handleMonthlyDrill = () => {
    const mData = monthlyRevenueForChart || monthlyRevenue
    if (!mData?.length) return
    openPanel({
      title:    'Monthly Revenue Trend',
      subtitle: activePlatform !== 'All' ? `${activePlatform} · ${activeYear !== 'All' ? activeYear : 'All years'}` : 'Revenue and profit by month',
      rows: [...mData].reverse(),
      columns: [
        { key: 'month_name',       label: 'Month',      align: 'left' },
        { key: 'year',             label: 'Year',       mono: true    },
        { key: 'monthly_revenue',  label: 'Revenue',    format: 'currency', bar: true, barColor: '#0ea5e9' },
        { key: 'monthly_profit',   label: 'Profit',     format: 'currency' },
        { key: 'monthly_ad_spend', label: 'Ad Spend',   format: 'currency' },
        { key: 'campaigns_run',    label: 'Campaigns',  format: 'num', mono: true },
      ],
    })
  }

  return (
    <div>
      {/* KPI Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '10px', marginBottom: '16px',
      }}>
        <KPICard
          label="TOTAL REVENUE"
          value={kpis ? fmt.currency(kpis.totalRevenue) : '—'}
          sub="▲ All platforms combined"
          subColor="#22c55e"
          icon="💰" iconBg="rgba(34,197,94,0.12)"
          sparkData={revenueSparkData} sparkColor="#0ea5e9"
          onClick={handlePlatformDrill}
        />
        <KPICard
          label="TOTAL PROFIT"
          value={kpis ? fmt.currency(kpis.totalProfit) : '—'}
          sub="Net after ad spend"
          subColor="#94a3b8"
          icon="📈" iconBg="rgba(14,165,233,0.12)"
          sparkData={profitSparkData} sparkColor="#22c55e"
          onClick={handlePlatformDrill}
        />
        <KPICard
          label="AVG ROAS"
          value={kpis ? fmt.roas(kpis.avgROAS) : '—'}
          sub="Return on ad spend"
          subColor="#94a3b8"
          icon="🎯" iconBg="rgba(245,158,11,0.12)"
          onClick={handlePlatformDrill}
        />
        <KPICard
          label="TOTAL CAMPAIGNS"
          value={kpis ? fmt.count(kpis.totalCampaigns) : '—'}
          sub="Across all platforms"
          subColor="#94a3b8"
          icon="📣" iconBg="rgba(139,92,246,0.12)"
          onClick={handlePlatformDrill}
        />
      </div>

      {/* ML Forecast strip */}
      {forecast?.forecasts && (
        <div style={{
          background: 'rgba(14,165,233,0.04)',
          border: '1px solid rgba(14,165,233,0.12)',
          borderRadius: '10px', padding: '10px 16px',
          marginBottom: '16px', display: 'flex',
          gap: '8px', flexWrap: 'wrap', alignItems: 'center',
        }}>
          <span style={{
            fontSize: '10px', color: '#0ea5e9',
            fontFamily: 'DM Mono, monospace', marginRight: '4px',
          }}>
            ◈ ML Forecast · {forecast.next_period}:
          </span>
          {[
            ['avg_roi',      'ROI',     '',  'x'],
            ['avg_roas',     'ROAS',    '',  'x'],
            ['total_revenue','Revenue', '₹', 'M'],
          ].map(([key, label, pre, suf]) => {
            const f = forecast.forecasts[key]
            if (!f || f.error) return null
            const isUp = f.predicted_value >= f.current_value
            return (
              <span key={key} style={{
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.07)',
                borderRadius: '6px', padding: '3px 10px',
                fontSize: '10px', fontFamily: 'DM Mono, monospace', color: '#94a3b8',
              }}>
                {label}: <span style={{ color: isUp ? '#4ade80' : '#f87171' }}>
                  {isUp ? '▲' : '▼'} {pre}
                  {key === 'total_revenue'
                    ? (f.predicted_value / 1e6).toFixed(1) + suf
                    : f.predicted_value.toFixed(2) + suf}
                </span>
              </span>
            )
          })}
        </div>
      )}

      {/* Charts Row 1: Donut + Monthly */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1.6fr',
        gap: '12px', marginBottom: '12px',
      }}>
        <ChartCard
          title="Total Revenue by Platform"
          subtitle={activePlatform === 'All' ? 'Share of revenue per channel' : `${activePlatform} only`}
          onClick={handlePlatformDrill}
        >
          <DonutChart data={filteredPlatformData} />
        </ChartCard>

        <ChartCard
          title="Total Revenue by Month"
          subtitle="Monthly revenue vs profit trend"
          onClick={handleMonthlyDrill}
        >
          <MonthlyAreaChart data={monthlyRevenueForChart || monthlyRevenue} />
        </ChartCard>
      </div>

      {/* Charts Row 2: Category bar + Key Insights */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1.6fr 1fr',
        gap: '12px',
      }}>
        <ChartCard
          title="Total Revenue by Business Category"
          subtitle="Top 10 categories by revenue"
          onClick={handleCategoryDrill}
        >
          <CategoryBarChart data={revenueByCategoryForChart || revenueByCategory} />
        </ChartCard>

        <KeyInsights
          revenueByPlatform={revenueByPlatform}
          monthlyRevenue={monthlyRevenue}
          revenueByCategory={revenueByCategory}
        />
      </div>
    </div>
  )
}