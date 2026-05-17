/**
 * useChatHistory.js
 *
 * Manages the sidebar conversation history list.
 * Stored in localStorage so it persists across page reloads.
 *
 * Each history entry:
 * {
 *   id:        string  — session_id from backend
 *   title:     string  — first user message (truncated)
 *   ts:        number  — timestamp of creation
 *   preview:   string  — first AI response snippet
 * }
 */

import { useState, useCallback, useEffect } from 'react'

const STORAGE_KEY = 'sma_chat_history'
const MAX_ENTRIES = 40

function load() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

function save(entries) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(entries))
  } catch {}
}

export function useChatHistory() {
  const [history, setHistory] = useState(load)

  // Persist on every change
  useEffect(() => {
    save(history)
  }, [history])

  // Add or update an entry
  const upsertEntry = useCallback((sessionId, firstUserMsg, firstAiMsg) => {
    setHistory(prev => {
      const existing = prev.findIndex(e => e.id === sessionId)
      const entry = {
        id:      sessionId,
        title:   firstUserMsg.length > 52
          ? firstUserMsg.slice(0, 52) + '…'
          : firstUserMsg,
        preview: firstAiMsg
          ? firstAiMsg.replace(/[#*`]/g, '').slice(0, 80) + '…'
          : '',
        ts: existing === -1 ? Date.now() : prev[existing].ts,
      }
      if (existing !== -1) {
        const updated = [...prev]
        updated[existing] = entry
        return updated
      }
      // Prepend new, cap at MAX_ENTRIES
      return [entry, ...prev].slice(0, MAX_ENTRIES)
    })
  }, [])

  // Remove one entry (when user deletes a chat)
  const removeEntry = useCallback((sessionId) => {
    setHistory(prev => prev.filter(e => e.id !== sessionId))
  }, [])

  // Clear all
  const clearAll = useCallback(() => {
    setHistory([])
  }, [])

  return { history, upsertEntry, removeEntry, clearAll }
}