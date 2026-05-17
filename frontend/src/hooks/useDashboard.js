/**
 * useDashboard.js
 *
 * Fetches all dashboard data from FastAPI.
 * Handles loading, error, and refresh states.
 * Matches the pattern of useChat.js exactly.
 */

import { useState, useEffect, useCallback } from 'react'
import {
  fetchRevenueByPlatform,
  fetchMonthlyRevenue,
  fetchCampaignPerformance,
  fetchAudienceAgeGroups,
  fetchConversionFunnel,
  fetchSmartAlerts,
  fetchMLForecast,
} from '../services/api'

const PLATFORMS = ['All', 'Instagram', 'Facebook', 'YouTube', 'LinkedIn', 'WhatsApp Business']

export function useDashboard() {
  const [activePlatform, setActivePlatform] = useState('All')
  const [activeTab,      setActiveTab]      = useState('overview')
  const [isLoading,      setIsLoading]      = useState(true)
  const [lastRefreshed,  setLastRefreshed]  = useState(null)
  const [error,          setError]          = useState(null)

  // Data state
  const [revenueByPlatform,  setRevenueByPlatform]  = useState([])
  const [monthlyRevenue,     setMonthlyRevenue]      = useState([])
  const [campaignData,       setCampaignData]        = useState([])
  const [audienceData,       setAudienceData]        = useState([])
  const [funnelData,         setFunnelData]          = useState([])
  const [alerts,             setAlerts]              = useState(null)
  const [forecast,           setForecast]            = useState(null)

  const fetchAll = useCallback(async (platform = null) => {
    setIsLoading(true)
    setError(null)

    try {
      const [rev, monthly, campaigns, audience, funnel, alertData, forecastData] =
        await Promise.all([
          fetchRevenueByPlatform(),
          fetchMonthlyRevenue(),
          fetchCampaignPerformance(platform === 'All' ? null : platform),
          fetchAudienceAgeGroups(),
          fetchConversionFunnel(),
          fetchSmartAlerts(),
          fetchMLForecast(platform === 'All' ? null : platform),
        ])

      setRevenueByPlatform(rev   || [])
      setMonthlyRevenue(monthly  || [])
      setCampaignData(campaigns  || [])
      setAudienceData(audience   || [])
      setFunnelData(funnel       || [])
      setAlerts(alertData        || null)
      setForecast(forecastData   || null)
      setLastRefreshed(new Date())

    } catch (err) {
      setError(err.message || 'Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Initial load
  useEffect(() => {
    fetchAll(activePlatform)
  }, [])

  // Reload when platform changes
  const handlePlatformChange = useCallback((platform) => {
    setActivePlatform(platform)
    fetchAll(platform)
  }, [fetchAll])

  const refresh = useCallback(() => {
    fetchAll(activePlatform)
  }, [fetchAll, activePlatform])

  // ── Derived KPIs ──────────────────────────────────────────
  // Computed from raw API data — no hardcoding
const kpis = (() => {
  if (!revenueByPlatform.length) return null

  const filtered = activePlatform === 'All'
    ? revenueByPlatform
    : revenueByPlatform.filter(r => r.platform === activePlatform)

  // ✅ parseFloat() prevents string concatenation from NUMERIC fields
  const totalRevenue   = filtered.reduce((s, r) => s + (parseFloat(r.total_revenue)  || 0), 0)
  const totalSpend     = filtered.reduce((s, r) => s + (parseFloat(r.total_ad_spend) || 0), 0)
  const totalCampaigns = filtered.reduce((s, r) => s + (parseFloat(r.total_campaigns)|| 0), 0)
  const avgROAS        = filtered.length
    ? filtered.reduce((s, r) => s + (parseFloat(r.avg_roas) || 0), 0) / filtered.length
    : 0
  const avgROI         = filtered.length
    ? filtered.reduce((s, r) => s + (parseFloat(r.avg_roi)  || 0), 0) / filtered.length
    : 0

  return { totalRevenue, totalSpend, totalCampaigns, avgROAS, avgROI }
})()
  

  return {
    // State
    activePlatform,
    activeTab,
    isLoading,
    lastRefreshed,
    error,
    platforms: PLATFORMS,

    // Data
    revenueByPlatform,
    monthlyRevenue,
    campaignData,
    audienceData,
    funnelData,
    alerts,
    forecast,
    kpis,

    // Actions
    setActiveTab,
    handlePlatformChange,
    refresh,
  }
}