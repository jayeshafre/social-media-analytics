/**
 * api.js — Service layer for FastAPI communication.
 *
 * All backend calls live here.
 * Components never call axios directly.
 */

import axios from 'axios'

const BASE_URL = 'http://localhost:8000/api/v1'

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000,
})

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

// ── Dashboard API calls ───────────────────────────────────────

export async function fetchRevenueByPlatform() {
  const response = await client.get('/revenue/by-platform')
  return response.data.data
}

export async function fetchMonthlyRevenue() {
  const response = await client.get('/revenue/monthly-trend')
  return response.data.data
}

export async function fetchCampaignPerformance(platform = null) {
  const params = platform ? { platform } : {}
  const response = await client.get('/campaigns/performance-by-type', { params })
  return response.data.data
}

export async function fetchPlatformComparison() {
  const response = await client.get('/platform/comparison')
  return response.data.data
}

export async function fetchAudienceAgeGroups() {
  const response = await client.get('/audience/by-age-group')
  return response.data.data
}

export async function fetchConversionFunnel() {
  const response = await client.get('/intelligence/conversion-funnel')
  return response.data.data
}

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