/**
 * api.js — Service layer for FastAPI communication.
 *
 * All backend calls are centralised here.
 * Components never call axios directly — they call these functions.
 * This mirrors the separation-of-concerns pattern in your FastAPI backend.
 */

import axios from 'axios'

const BASE_URL = 'http://localhost:8000/api/v1'

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000, // 60s — LLM responses can be slow
})

/**
 * Send a chat message to the AI orchestrator.
 *
 * @param {string} message       - User's question
 * @param {string|null} sessionId - Existing session ID for continuity
 * @returns {Promise<object>}     - Full response data object from FastAPI
 */
export async function sendChatMessage(message, sessionId = null) {
  const payload = { message }
  if (sessionId) payload.session_id = sessionId

  const response = await client.post('/ai/chat', payload)
  return response.data.data // unwrap APIResponse wrapper
}

/**
 * Create a fresh session ID before the first message.
 * Useful for pre-warming sessions on panel open.
 *
 * @returns {Promise<string>} - New session ID string
 */
export async function createNewSession() {
  const response = await client.post('/ai/session/new')
  return response.data.data.session_id
}

/**
 * Clear conversation history for a session (user presses "New Chat").
 *
 * @param {string} sessionId
 * @returns {Promise<boolean>}
 */
export async function clearSession(sessionId) {
  await client.delete(`/ai/session/${sessionId}`)
  return true
}

/**
 * Health check — used to show backend connectivity status in UI.
 *
 * @returns {Promise<object>} - { api, database, redis, environment }
 */
export async function checkHealth() {
  const response = await client.get('/../../health') // /health is at root
  return response.data
}