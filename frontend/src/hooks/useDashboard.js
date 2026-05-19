

import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  fetchRevenueByPlatform,
  fetchMonthlyRevenue,
  fetchCampaignPerformance,
  fetchCampaignByObjective,
  fetchInfluencerImpact,
  fetchAudienceAgeGroups,
  fetchAudienceByDevice,
  fetchAudienceByGender,
  fetchConversionFunnel,
  fetchCACByPlatform,
  fetchYoYGrowth,
  fetchRefundAnalysis,
  fetchPlatformVsBenchmark,
  fetchPlatformRevenueShare,
  fetchBestPlatformPerCategory,
  fetchSentimentByPlatform,
  fetchEngagementProgression,
  fetchRevenueByCategory,
  fetchRevenueByCategoryPlatform,
  fetchRevenueByCategoryPlatformYear,
  fetchCampaignsByPlatformYear,
  fetchSmartAlerts,
  fetchMLForecast,
} from '../services/api'

const PLATFORMS = ['All', 'Instagram', 'Facebook', 'YouTube', 'LinkedIn', 'WhatsApp Business']
const YEARS     = ['All', '2024', '2023', '2022', '2021', '2020', '2019']
const TABS      = ['executive', 'campaign', 'platform', 'audience', 'alerts']

export function useDashboard() {
  const [activePlatform, setActivePlatform] = useState('All')
  const [activeYear,     setActiveYear]     = useState('All')
  const [activeTab,      setActiveTab]      = useState('executive')
  const [isLoading,      setIsLoading]      = useState(true)
  const [lastRefreshed,  setLastRefreshed]  = useState(null)
  const [error,          setError]          = useState(null)

  // ── Raw data ──────────────────────────────────────────────
  const [revenueByPlatform,       setRevenueByPlatform]       = useState([])
  const [monthlyRevenue,          setMonthlyRevenue]           = useState([])
  const [revenueByCategory,       setRevenueByCategory]        = useState([])
  const [revenueByCategoryPlatform, setRevenueByCategoryPlatform] = useState([])
  const [revenueByCategoryPlatformYear, setRevenueByCategoryPlatformYear] = useState([])
  const [campaignData,            setCampaignData]             = useState([])
  const [campaignByObjective,     setCampaignByObjective]      = useState([])
  const [influencerData,          setInfluencerData]           = useState([])
  const [audienceAge,             setAudienceAge]              = useState([])
  const [audienceDevice,          setAudienceDevice]           = useState([])
  const [audienceGender,          setAudienceGender]           = useState([])
  const [funnelData,              setFunnelData]               = useState([])
  const [cacData,                 setCacData]                  = useState([])
  const [yoyData,                 setYoyData]                  = useState([])
  const [campaignsByPlatformYear, setCampaignsByPlatformYear]  = useState([])
  const [refundData,              setRefundData]               = useState([])
  const [platformBenchmark,       setPlatformBenchmark]        = useState([])
  const [platformRevenueShare,    setPlatformRevenueShare]     = useState([])
  const [bestPlatformByCategory,  setBestPlatformByCategory]   = useState([])
  const [sentimentData,           setSentimentData]            = useState([])
  const [engagementProgression,   setEngagementProgression]    = useState([])
  const [alerts,                  setAlerts]                   = useState(null)
  const [forecast,                setForecast]                 = useState(null)

  const fetchAll = useCallback(async (platform = 'All', year = 'All') => {
    setIsLoading(true)
    setError(null)
    const p = platform === 'All' ? null : platform
    const y = year === 'All' ? null : parseInt(year)

    try {
      const [
        rev, monthly, revCat, revCatPlatform,
        campaigns, objective, influencer,
        ageGroups, devices, gender,
        funnel, cac, yoy, refund,
        benchmark, revShare, bestPlatform,
        sentiment, engagement,
        alertData, forecastData,
      ] = await Promise.allSettled([
        fetchRevenueByPlatform(),
        fetchMonthlyRevenue(y),
        fetchRevenueByCategory(),
        fetchRevenueByCategoryPlatform(),
        fetchCampaignPerformance(p),
        fetchCampaignByObjective(),
        fetchInfluencerImpact(),
        fetchAudienceAgeGroups(),
        fetchAudienceByDevice(),
        fetchAudienceByGender(),
        fetchConversionFunnel(),
        fetchCACByPlatform(),
        fetchYoYGrowth(),
        fetchRefundAnalysis(),
        fetchPlatformVsBenchmark(),
        fetchPlatformRevenueShare(),
        fetchBestPlatformPerCategory(),
        fetchSentimentByPlatform(),
        fetchEngagementProgression(),
        fetchSmartAlerts(),
        fetchMLForecast(p),
      ])

      const val = (r, fallback = []) => r.status === 'fulfilled' ? (r.value ?? fallback) : fallback

      setRevenueByPlatform(val(rev))
      setMonthlyRevenue(val(monthly))
      setRevenueByCategory(val(revCat))
      setRevenueByCategoryPlatform(val(revCatPlatform))
      setCampaignData(val(campaigns))
      setCampaignByObjective(val(objective))
      setInfluencerData(val(influencer))
      setAudienceAge(val(ageGroups))
      setAudienceDevice(val(devices))
      setAudienceGender(val(gender))
      setFunnelData(val(funnel))
      setCacData(val(cac))
      setYoyData(val(yoy))
      setRefundData(val(refund))
      setPlatformBenchmark(val(benchmark))
      setPlatformRevenueShare(val(revShare))
      setBestPlatformByCategory(val(bestPlatform))
      setSentimentData(val(sentiment))
      setEngagementProgression(val(engagement))
      setAlerts(alertData.status === 'fulfilled' ? alertData.value : null)
      setForecast(forecastData.status === 'fulfilled' ? forecastData.value : null)
      setLastRefreshed(new Date())

    } catch (err) {
      setError(err.message || 'Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => { fetchAll(activePlatform) }, [])

  // Static datasets: fetched ONCE on mount — always return all platforms+all years
  // Client-side filtering handles all slicing — no re-fetch ever needed
  useEffect(() => {
    fetchCampaignsByPlatformYear()
      .then(data => setCampaignsByPlatformYear(data || []))
      .catch(() => setCampaignsByPlatformYear([]))
    fetchRevenueByCategoryPlatformYear()
      .then(data => setRevenueByCategoryPlatformYear(data || []))
      .catch(() => setRevenueByCategoryPlatformYear([]))
  }, [])


  const handlePlatformChange = useCallback((platform) => {
    setActivePlatform(platform)
    fetchAll(platform, activeYear)
  }, [fetchAll, activeYear])

  const handleYearChange = useCallback((year) => {
    setActiveYear(year)
    fetchAll(activePlatform, year)
  }, [fetchAll, activePlatform])

  const refresh = useCallback(() => {
    fetchAll(activePlatform, activeYear)
  }, [fetchAll, activePlatform, activeYear])

  // ── Derived KPIs — filtered by BOTH activePlatform AND activeYear ──
  // Source: campaignsByPlatformYear which has platform + year + month columns
  // Falls back to revenueByPlatform when no year filter (for ROAS/ROI averages)
  const kpis = (() => {
    if (!campaignsByPlatformYear.length && !revenueByPlatform.length) return null

    // Filter the granular dataset by platform and year
    let rows = campaignsByPlatformYear
    if (activePlatform !== 'All') {
      rows = rows.filter(r => r.platform === activePlatform)
    }
    if (activeYear !== 'All') {
      rows = rows.filter(r => String(r.year) === String(activeYear))
    }

    // If granular data exists, compute from it
    if (rows.length) {
      const totalRevenue   = rows.reduce((s, r) => s + (parseFloat(r.total_revenue)  || 0), 0)
      const totalProfit    = rows.reduce((s, r) => s + (parseFloat(r.total_profit)   || 0), 0)
      const totalSpend     = rows.reduce((s, r) => s + (parseFloat(r.total_ad_spend) || 0), 0)
      const totalCampaigns = rows.reduce((s, r) => s + (parseFloat(r.total_campaigns)|| 0), 0)
      const avgROAS        = rows.length
        ? rows.reduce((s, r) => s + (parseFloat(r.avg_roas) || 0), 0) / rows.length : 0
      return { totalRevenue, totalProfit, totalSpend, totalCampaigns, avgROAS, avgROI: 0 }
    }

    // Fallback: use revenueByPlatform (all years) filtered by platform only
    const fallback = activePlatform === 'All'
      ? revenueByPlatform
      : revenueByPlatform.filter(r => r.platform === activePlatform)
    const totalRevenue   = fallback.reduce((s, r) => s + (parseFloat(r.total_revenue)  || 0), 0)
    const totalProfit    = fallback.reduce((s, r) => s + (parseFloat(r.total_profit)   || 0), 0)
    const totalSpend     = fallback.reduce((s, r) => s + (parseFloat(r.total_ad_spend) || 0), 0)
    const totalCampaigns = fallback.reduce((s, r) => s + (parseFloat(r.total_campaigns)|| 0), 0)
    const avgROAS        = fallback.length
      ? fallback.reduce((s, r) => s + (parseFloat(r.avg_roas) || 0), 0) / fallback.length : 0
    const avgROI         = fallback.length
      ? fallback.reduce((s, r) => s + (parseFloat(r.avg_roi)  || 0), 0) / fallback.length : 0
    return { totalRevenue, totalProfit, totalSpend, totalCampaigns, avgROAS, avgROI }
  })()

  // monthlyRevenue is already server-filtered by year via fetchMonthlyRevenue(year)
  const filteredMonthly = monthlyRevenue

  // ── filteredMonthlyForChart ───────────────────────────────────────────────
  // useMemo ensures this only recomputes when its actual dependencies change.
  // activePlatform === 'All': use monthlyRevenue (server already year-filtered by fetchAll)
  // specific platform: filter campaignsByPlatformYear client-side (full dataset, always loaded)
  const filteredMonthlyForChart = useMemo(() => {
    if (activePlatform === 'All') {
      // Server already filtered by year — just return as-is
      return monthlyRevenue.length ? monthlyRevenue : []
    }

    // campaignsByPlatformYear has all platforms + all years — filter client-side
    let rows = campaignsByPlatformYear.filter(r => r.platform === activePlatform)
    if (activeYear !== 'All') {
      rows = rows.filter(r => String(r.year) === String(activeYear))
    }

    if (!rows.length) return []

    // Aggregate by month — normalise column names to monthly_* for MonthlyAreaChart
    const byMonth = {}
    rows.forEach(r => {
      const key = `${r.year}-${String(r.month).padStart(2, '0')}`
      if (!byMonth[key]) {
        byMonth[key] = {
          year: r.year, month: r.month, month_name: r.month_name,
          monthly_revenue: 0, monthly_profit: 0,
          monthly_ad_spend: 0, campaigns_run: 0,
        }
      }
      byMonth[key].monthly_revenue  += parseFloat(r.total_revenue)  || 0
      byMonth[key].monthly_profit   += parseFloat(r.total_profit)   || 0
      byMonth[key].monthly_ad_spend += parseFloat(r.total_ad_spend) || 0
      byMonth[key].campaigns_run    += parseFloat(r.total_campaigns) || 0
    })
    return Object.values(byMonth).sort((a, b) =>
      a.year !== b.year ? a.year - b.year : a.month - b.month)
  }, [activePlatform, activeYear, monthlyRevenue, campaignsByPlatformYear])

  // ── filteredCategoryForChart ──────────────────────────────────────────────
  // Source: revenueByCategoryPlatformYear — has platform + category + year + revenue
  // This is REAL data, no scaling/approximation.
  // Filters applied client-side for instant response without extra API calls.
  const filteredCategoryForChart = (() => {
    // Case 1: No filters at all — use simple revenueByCategory (all platforms, all years)
    if (activePlatform === 'All' && activeYear === 'All') return revenueByCategory

    // Case 2: Platform filter only (no year) — use revenueByCategoryPlatform
    if (activePlatform !== 'All' && activeYear === 'All') {
      return revenueByCategoryPlatform
        .filter(r => r.platform === activePlatform)
        .sort((a, b) => parseFloat(b.total_revenue) - parseFloat(a.total_revenue))
    }

    // Case 3: Year filter only (no platform) — aggregate across all platforms for that year
    if (activePlatform === 'All' && activeYear !== 'All') {
      const rows = revenueByCategoryPlatformYear.filter(r => String(r.year) === String(activeYear))
      // Group by business_category and sum across platforms
      const byCategory = {}
      rows.forEach(r => {
        const cat = r.business_category
        if (!byCategory[cat]) byCategory[cat] = {
          business_category: cat,
          total_revenue: 0, total_profit: 0,
          total_campaigns: 0, avg_roi: 0, avg_roas: 0, _count: 0,
        }
        byCategory[cat].total_revenue  += parseFloat(r.total_revenue)  || 0
        byCategory[cat].total_profit   += parseFloat(r.total_profit)   || 0
        byCategory[cat].total_campaigns += parseFloat(r.total_campaigns) || 0
        byCategory[cat].avg_roi        += parseFloat(r.avg_roi)        || 0
        byCategory[cat].avg_roas       += parseFloat(r.avg_roas)       || 0
        byCategory[cat]._count         += 1
      })
      return Object.values(byCategory).map(r => ({
        ...r,
        avg_roi:  r._count > 0 ? r.avg_roi  / r._count : 0,
        avg_roas: r._count > 0 ? r.avg_roas / r._count : 0,
      })).sort((a, b) => parseFloat(b.total_revenue) - parseFloat(a.total_revenue))
    }

    // Case 4: Both platform AND year selected — direct filter from granular dataset
    return revenueByCategoryPlatformYear
      .filter(r =>
        r.platform === activePlatform &&
        String(r.year) === String(activeYear)
      )
      .sort((a, b) => parseFloat(b.total_revenue) - parseFloat(a.total_revenue))
  })()

  return {
    // Filters
    activePlatform, activeYear, activeTab,
    isLoading, lastRefreshed, error,
    platforms: PLATFORMS, years: YEARS, tabs: TABS,

    // Data
    revenueByPlatform, monthlyRevenue: filteredMonthly,
    monthlyRevenueForChart: filteredMonthlyForChart,
    revenueByCategory, revenueByCategoryForChart: filteredCategoryForChart,
    revenueByCategoryPlatform, revenueByCategoryPlatformYear,
    campaignData, campaignByObjective, influencerData,
    audienceAge, audienceDevice, audienceGender,
    funnelData, cacData, yoyData, refundData,
    platformBenchmark, platformRevenueShare, bestPlatformByCategory,
    sentimentData, engagementProgression,
    alerts, forecast, kpis,

    // Actions
    setActiveTab,
    handlePlatformChange,
    handleYearChange,
    refresh,
  }
}