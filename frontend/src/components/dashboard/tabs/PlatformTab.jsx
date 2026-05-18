/**
 * tabs/PlatformTab.jsx
 *
 * Platform Comparison — mirrors Page 3 of your Power BI dashboard:
 * - KPI highlight cards: Best ROAS, Lowest CAC, Highest CTR, Best Funnel
 * - CTR vs Market Benchmark (diverging bar chart)
 * - Platform Performance Matrix (table with conditional formatting)
 * - Revenue & Spend share (stacked bar)
 * - Conversion funnel flow
 * - YoY Revenue Growth
 * - Customer Acquisition Cost by Platform
 * - Best Platform per Business Category
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
  return PLATFORM_COLORS[platform] || ['#0ea5e9','#8b5cf6','#22c55e','#f59e0b','#ef4444'][i % 5]
}

const fmt = {
  pct2: v => parseFloat(v).toFixed(2) + '%',
  roas: v => parseFloat(v).toFixed(2) + 'x',
  curr: v => '₹' + Number(Math.round(parseFloat(v))).toLocaleString('en-IN'),
  num:  v => Number(Math.round(parseFloat(v))).toLocaleString('en-IN'),
}

// ── CTR vs Benchmark diverging bar ───────────────────────────
function BenchmarkChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const sorted = [...data].sort((a, b) =>
      parseFloat(b.ctr_vs_benchmark_pct) - parseFloat(a.ctr_vs_benchmark_pct))
    const labels  = sorted.map(r => r.platform)
    const ourCTR  = sorted.map(r => parseFloat((parseFloat(r.our_avg_ctr) * 100).toFixed(3)))
    const mktCTR  = sorted.map(r => parseFloat((parseFloat(r.avg_market_ctr) * 100).toFixed(3)))

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Our CTR', data: ourCTR,
            backgroundColor: labels.map(l => getColor(l, 0)),
            borderRadius: 4,
          },
          {
            label: 'Market Benchmark', data: mktCTR,
            backgroundColor: 'rgba(239,68,68,0.6)',
            borderRadius: 4,
          },
        ],
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
    <>
      <div style={{ display: 'flex', gap: '14px', marginBottom: '8px' }}>
        {[{ color: '#0ea5e9', label: 'Our CTR' }, { color: '#ef4444', label: 'Market Benchmark' }].map(({ color, label }) => (
          <span key={label} style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            fontSize: '10px', color: '#475569', fontFamily: 'DM Mono, monospace',
          }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: color, display: 'inline-block' }} />
            {label}
          </span>
        ))}
      </div>
      <div style={{ position: 'relative', height: '180px' }}>
        <canvas ref={ref} role="img" aria-label="Our CTR vs market benchmark per platform" />
      </div>
    </>
  )
}

// ── YoY Growth chart ─────────────────────────────────────────
function YoYChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const filtered = data.filter(r => r.yoy_growth_pct !== null)
    const labels = filtered.map(r => String(r.year))
    const values = filtered.map(r => parseFloat(parseFloat(r.yoy_growth_pct).toFixed(2)))

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: values.map(v => v >= 0 ? 'rgba(34,197,94,0.7)' : 'rgba(239,68,68,0.7)'),
          borderRadius: 5,
        }],
      },
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

  return (
    <div style={{ position: 'relative', height: '160px' }}>
      <canvas ref={ref} role="img" aria-label="Year over year revenue growth chart" />
    </div>
  )
}

// ── CAC by platform horizontal bar ───────────────────────────
function CACChart({ data }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !data?.length || !window.Chart) return
    if (chartRef.current) chartRef.current.destroy()

    const sorted = [...data].sort((a, b) => parseFloat(a.cac) - parseFloat(b.cac))
    const labels = sorted.map(r => r.platform)
    const values = sorted.map(r => parseFloat(parseFloat(r.cac).toFixed(2)))

    chartRef.current = new window.Chart(ref.current, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: labels.map((l, i) => getColor(l, i)),
          borderRadius: 5,
        }],
      },
      options: {
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: {
            ticks: { callback: v => '₹' + v, color: '#475569', font: { size: 10 } },
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
      <canvas ref={ref} role="img" aria-label="Customer acquisition cost by platform" />
    </div>
  )
}

// ── Platform Performance Matrix table ────────────────────────
function PlatformMatrix({ data }) {
  if (!data?.length) return null

  const maxROAS = Math.max(...data.map(r => parseFloat(r.avg_roas) || 0))
  const maxCTR  = Math.max(...data.map(r => parseFloat(r.our_avg_ctr) || 0))

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '11px' }}>
        <thead>
          <tr>
            {['Platform', 'Avg ROAS', 'Avg CTR', 'Avg CPC', 'Campaigns'].map(h => (
              <th key={h} style={{
                textAlign: h === 'Platform' ? 'left' : 'right',
                padding: '6px 10px', color: '#334155',
                fontFamily: 'DM Mono, monospace', fontSize: '9px',
                textTransform: 'uppercase', letterSpacing: '0.06em',
                borderBottom: '1px solid rgba(255,255,255,0.07)',
              }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => {
            const isTopROAS = parseFloat(row.avg_roas)    === maxROAS
            const isTopCTR  = parseFloat(row.our_avg_ctr) === maxCTR
            return (
              <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{
                  padding: '7px 10px', fontFamily: 'Syne, sans-serif',
                  color: getColor(row.platform, i), fontWeight: 600,
                }}>
                  {row.platform}
                </td>
                <td style={{
                  padding: '7px 10px', textAlign: 'right',
                  fontFamily: 'DM Mono, monospace',
                  color: isTopROAS ? '#4ade80' : '#64748b',
                  fontWeight: isTopROAS ? 700 : 400,
                }}>
                  {fmt.roas(row.avg_roas)}
                  {isTopROAS && <span style={{ marginLeft: '4px', fontSize: '9px', color: '#4ade80' }}>★</span>}
                </td>
                <td style={{
                  padding: '7px 10px', textAlign: 'right',
                  fontFamily: 'DM Mono, monospace',
                  color: isTopCTR ? '#fbbf24' : '#64748b',
                  fontWeight: isTopCTR ? 700 : 400,
                }}>
                  {(parseFloat(row.our_avg_ctr) * 100).toFixed(2)}%
                  {isTopCTR && <span style={{ marginLeft: '4px', fontSize: '9px', color: '#fbbf24' }}>★</span>}
                </td>
                <td style={{ padding: '7px 10px', textAlign: 'right', fontFamily: 'DM Mono, monospace', color: '#64748b' }}>
                  ₹{parseFloat(row.our_avg_cpc).toFixed(2)}
                </td>
                <td style={{ padding: '7px 10px', textAlign: 'right', fontFamily: 'DM Mono, monospace', color: '#475569' }}>
                  {fmt.num(row.total_campaigns)}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      <div style={{ fontSize: '9px', color: '#1e3a5f', fontFamily: 'DM Mono, monospace', marginTop: '6px' }}>
        ★ = best in column
      </div>
    </div>
  )
}

// ── Platform Tab ──────────────────────────────────────────────
export default function PlatformTab({
  platformBenchmark, platformRevenueShare, bestPlatformByCategory,
  cacData, yoyData, openPanel,
}) {
  const bestROAS  = platformBenchmark?.reduce((a, b) =>
    parseFloat(b.avg_roas) > parseFloat(a?.avg_roas || 0) ? b : a, null)
  const lowestCAC = cacData?.reduce((a, b) =>
    parseFloat(b.cac) < parseFloat(a?.cac || Infinity) ? b : a, null)
  const bestCTR   = platformBenchmark?.reduce((a, b) =>
    parseFloat(b.ctr_vs_benchmark_pct) > parseFloat(a?.ctr_vs_benchmark_pct || -Infinity) ? b : a, null)

  const handleBenchmarkDrill = () => {
    if (!platformBenchmark?.length) return
    openPanel({
      title:    'Platform vs Market Benchmark',
      subtitle: 'Our CTR and CPC vs industry averages',
      rows:     platformBenchmark,
      columns: [
        { key: 'platform',              label: 'Platform',       align: 'left' },
        { key: 'our_avg_ctr',           label: 'Our CTR',        format: 'pct2', bar: true, barColor: '#0ea5e9' },
        { key: 'avg_market_ctr',        label: 'Market CTR',     format: 'pct2', mono: true },
        { key: 'ctr_vs_benchmark_pct',  label: 'vs Benchmark',   format: 'pct2', mono: true },
        { key: 'our_avg_cpc',           label: 'Our CPC',        mono: true },
        { key: 'avg_roas',              label: 'ROAS',           format: 'roas', mono: true },
      ],
      note: 'Positive vs Benchmark % means our CTR outperforms the market average.',
    })
  }

  const handleCACDrill = () => {
    if (!cacData?.length) return
    openPanel({
      title:    'Customer Acquisition Cost (CAC) by Platform',
      subtitle: 'Lower CAC = more efficient customer acquisition',
      rows:     [...cacData].sort((a, b) => parseFloat(a.cac) - parseFloat(b.cac)),
      columns: [
        { key: 'platform',        label: 'Platform',      align: 'left' },
        { key: 'cac',             label: 'CAC (₹)',       bar: true, barColor: '#f59e0b' },
        { key: 'total_ad_spend',  label: 'Ad Spend',      format: 'currency' },
        { key: 'new_customers',   label: 'New Customers', format: 'num', mono: true },
        { key: 'total_conversions',label: 'Conversions',  format: 'num', mono: true },
      ],
    })
  }

  const handleCategoryDrill = () => {
    if (!bestPlatformByCategory?.length) return
    openPanel({
      title:    'Best Platform per Business Category',
      subtitle: 'Highest avg ROI platform for each category',
      rows:     bestPlatformByCategory,
      columns: [
        { key: 'business_category', label: 'Category',     align: 'left' },
        { key: 'best_platform',     label: 'Best Platform', align: 'left' },
        { key: 'avg_roi',           label: 'Avg ROI',      format: 'roas', mono: true, bar: true, barColor: '#22c55e' },
        { key: 'avg_roas',          label: 'Avg ROAS',     format: 'roas', mono: true },
        { key: 'campaigns',         label: 'Campaigns',    format: 'num',  mono: true },
      ],
    })
  }

  return (
    <div>
      {/* KPI highlight row */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '10px', marginBottom: '16px',
      }}>
        <KPICard
          label="BEST ROAS PLATFORM"
          value={bestROAS?.platform || '—'}
          sub={bestROAS ? fmt.roas(bestROAS.avg_roas) + ' avg ROAS' : ''}
          subColor="#22c55e"
          icon="🏆" iconBg="rgba(34,197,94,0.12)"
          onClick={handleBenchmarkDrill}
        />
        <KPICard
          label="LOWEST CAC"
          value={lowestCAC?.platform || '—'}
          sub={lowestCAC ? fmt.curr(lowestCAC.cac) + ' per customer' : ''}
          subColor="#22c55e"
          icon="💡" iconBg="rgba(245,158,11,0.12)"
          onClick={handleCACDrill}
        />
        <KPICard
          label="HIGHEST CTR VS BENCHMARK"
          value={bestCTR?.platform || '—'}
          sub={bestCTR ? '+' + parseFloat(bestCTR.ctr_vs_benchmark_pct).toFixed(1) + '% above market' : ''}
          subColor="#0ea5e9"
          icon="📡" iconBg="rgba(14,165,233,0.12)"
          onClick={handleBenchmarkDrill}
        />
        <KPICard
          label="PLATFORM CATEGORIES"
          value={String(bestPlatformByCategory?.length || 0)}
          sub="Unique business categories"
          icon="🗂" iconBg="rgba(139,92,246,0.12)"
          onClick={handleCategoryDrill}
        />
      </div>

      {/* Row 1: Benchmark + Matrix */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr',
        gap: '12px', marginBottom: '12px',
      }}>
        <ChartCard
          title="Our CTR vs Market Benchmark"
          subtitle="Performance above/below industry average"
          onClick={handleBenchmarkDrill}
        >
          <BenchmarkChart data={platformBenchmark} />
        </ChartCard>

        <ChartCard
          title="Platform Performance Matrix"
          subtitle="ROAS, CTR, CPC comparison · ★ = best in column"
          onClick={handleBenchmarkDrill}
        >
          <PlatformMatrix data={platformBenchmark} />
        </ChartCard>
      </div>

      {/* Row 2: YoY + CAC + Category */}
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
        gap: '12px',
      }}>
        <ChartCard
          title="Year-over-Year Revenue Growth"
          subtitle="Annual revenue growth rate"
        >
          <YoYChart data={yoyData} />
        </ChartCard>

        <ChartCard
          title="Customer Acquisition Cost"
          subtitle="CAC by platform — lower = better"
          onClick={handleCACDrill}
        >
          <CACChart data={cacData} />
        </ChartCard>

        <ChartCard
          title="Best Platform per Category"
          subtitle="Highest ROI platform for each vertical"
          onClick={handleCategoryDrill}
        >
          <div style={{ overflowY: 'auto', maxHeight: '180px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '11px' }}>
              <thead>
                <tr>
                  {['Category', 'Platform', 'ROI'].map(h => (
                    <th key={h} style={{
                      textAlign: 'left', padding: '4px 8px', color: '#334155',
                      fontFamily: 'DM Mono, monospace', fontSize: '9px',
                      textTransform: 'uppercase', letterSpacing: '0.06em',
                      borderBottom: '1px solid rgba(255,255,255,0.06)',
                      position: 'sticky', top: 0, background: 'rgba(8,13,24,0.95)',
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(bestPlatformByCategory || []).map((row, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                    <td style={{ padding: '5px 8px', color: '#94a3b8', fontFamily: 'Syne, sans-serif', fontSize: '11px' }}>
                      {row.business_category}
                    </td>
                    <td style={{ padding: '5px 8px', color: getColor(row.best_platform, i), fontFamily: 'Syne, sans-serif', fontSize: '11px', fontWeight: 600 }}>
                      {row.best_platform}
                    </td>
                    <td style={{ padding: '5px 8px', color: '#4ade80', fontFamily: 'DM Mono, monospace', fontSize: '10px' }}>
                      {fmt.roas(row.avg_roi)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </ChartCard>
      </div>
    </div>
  )
}