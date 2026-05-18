/**
 * api.js — Service layer for FastAPI communication.
 * All backend calls live here. Components never call axios directly.
 */

import axios from 'axios'

const BASE_URL = 'http://localhost:8000/api/v1'

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
})

// ── Chat ──────────────────────────────────────────────────────
export async function sendChatMessage(message, sessionId = null) {
  const payload = { message }
  if (sessionId) payload.session_id = sessionId
  const response = await client.post('/ai/chat', payload)
  return response.data.data
}
export async function createNewSession() {
  const response = await client.post('/ai/session/new')
  return response.data.data.session_id
}
export async function clearSession(sessionId) {
  await client.delete(`/ai/session/${sessionId}`)
  return true
}
export async function checkHealth() {
  const response = await axios.get('http://localhost:8000/health')
  return response.data
}

// ── Revenue ───────────────────────────────────────────────────
export async function fetchRevenueByPlatform() {
  const response = await client.get('/revenue/by-platform')
  return response.data.data
}
export async function fetchMonthlyRevenue(year = null) {
  const params = year ? { year } : {}
  const response = await client.get('/revenue/monthly-trend', { params })
  return response.data.data
}
export async function fetchRevenueByCategory() {
  const response = await client.get('/revenue/by-category')
  return response.data.data
}
export async function fetchRevenueBySeason() {
  const response = await client.get('/revenue/by-season')
  return response.data.data
}
export async function fetchTopCampaigns(limit = 10) {
  const response = await client.get('/revenue/top-campaigns', { params: { limit } })
  return response.data.data
}
export async function fetchRevenueByCategoryPlatform() {
  const response = await client.get('/revenue/by-category-platform')
  return response.data.data
}
export async function fetchRevenueByCategoryPlatformYear() {
  const response = await client.get('/revenue/by-category-platform-year')
  return response.data.data
}
export async function fetchCampaignsByPlatformYear() {
  const response = await client.get('/revenue/campaigns-by-platform-year')
  return response.data.data
}

// ── Campaigns ─────────────────────────────────────────────────
export async function fetchCampaignPerformance(platform = null) {
  const params = platform ? { platform } : {}
  const response = await client.get('/campaigns/performance-by-type', { params })
  return response.data.data
}
export async function fetchCampaignByObjective() {
  const response = await client.get('/campaigns/by-objective')
  return response.data.data
}
export async function fetchInfluencerImpact() {
  const response = await client.get('/campaigns/influencer-impact')
  return response.data.data
}

// ── Platforms ─────────────────────────────────────────────────
export async function fetchPlatformVsBenchmark() {
  const response = await client.get('/platforms/vs-benchmark')
  return response.data.data
}
export async function fetchPlatformRevenueShare() {
  const response = await client.get('/platforms/revenue-share')
  return response.data.data
}
export async function fetchBestPlatformPerCategory() {
  const response = await client.get('/platforms/best-per-category')
  return response.data.data
}

// ── Audience ──────────────────────────────────────────────────
export async function fetchAudienceAgeGroups() {
  const response = await client.get('/audience/by-age-group')
  return response.data.data
}
export async function fetchAudienceByDevice() {
  const response = await client.get('/audience/by-device')
  return response.data.data
}
export async function fetchAudienceByGender() {
  const response = await client.get('/audience/by-gender')
  return response.data.data
}
export async function fetchAudienceByIncomeLevel() {
  const response = await client.get('/audience/by-income-level')
  return response.data.data
}

// ── Intelligence ──────────────────────────────────────────────
export async function fetchConversionFunnel() {
  const response = await client.get('/intelligence/conversion-funnel')
  return response.data.data
}
export async function fetchCACByPlatform() {
  const response = await client.get('/intelligence/cac-by-platform')
  return response.data.data
}
export async function fetchYoYGrowth() {
  const response = await client.get('/intelligence/yoy-growth')
  return response.data.data
}
export async function fetchRefundAnalysis() {
  const response = await client.get('/intelligence/refund-analysis')
  return response.data.data
}

// ── Engagement ────────────────────────────────────────────────
export async function fetchSentimentByPlatform() {
  const response = await client.get('/engagement/sentiment-by-platform')
  return response.data.data
}
export async function fetchEngagementProgression() {
  const response = await client.get('/engagement/engagement-progression')
  return response.data.data
}

// ── AI / ML ───────────────────────────────────────────────────
export async function fetchSmartAlerts() {
  const response = await client.get('/ai/smart-alerts')
  return response.data.data
}
export async function fetchExecutiveSummary() {
  const response = await client.get('/ai/executive-summary')
  return response.data.data
}
export async function fetchMLForecast(platform = null) {
  const params = platform ? { platform } : {}
  const response = await client.get('/ai/ml/forecast', { params })
  return response.data.data
}