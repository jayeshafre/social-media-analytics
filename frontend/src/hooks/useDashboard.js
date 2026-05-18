/**
 * useDashboard.js
 *
 * Master hook — fetches all dashboard data from FastAPI.
 * Drives every tab: Executive, Campaign, Platform, Audience.
 * Handles loading, error, refresh, platform + year filters.
 */

import { useState, useEffect, useCallback } from 'react'
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
        rev, monthly, revCat,
        campaigns, objective, influencer,
        ageGroups, devices, gender,
        funnel, cac, yoy, refund,
        benchmark, revShare, bestPlatform,
        sentiment, engagement, campaignsPlatformYear,
        alertData, forecastData,
      ] = await Promise.allSettled([
        fetchRevenueByPlatform(),
        fetchMonthlyRevenue(y),
        fetchRevenueByCategory(),
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
        fetchCampaignsByPlatformYear(),
        fetchSmartAlerts(),
        fetchMLForecast(p),
      ])

      const val = (r, fallback = []) => r.status === 'fulfilled' ? (r.value ?? fallback) : fallback

      setRevenueByPlatform(val(rev))
      setMonthlyRevenue(val(monthly))
      setRevenueByCategory(val(revCat))
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
      setCampaignsByPlatformYear(val(campaignsPlatformYear))
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

  return {
    // Filters
    activePlatform, activeYear, activeTab,
    isLoading, lastRefreshed, error,
    platforms: PLATFORMS, years: YEARS, tabs: TABS,

    // Data
    revenueByPlatform, monthlyRevenue: filteredMonthly, revenueByCategory,
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