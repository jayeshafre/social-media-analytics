/**
 * useChat.js — Updated to pass terms_explained to message objects.
 *
 * Every AI message now carries a `terms` array (may be empty).
 * MessageBubble reads this to render the TermsGlossary section.
 */

import { useState, useCallback, useRef } from 'react'
import { sendChatMessage, clearSession } from '../services/api'

export function useChat({ onExchange } = {}) {
  const [messages, setMessages]   = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError]         = useState(null)
  const [lastMeta, setLastMeta]   = useState(null)

  const bottomRef       = useRef(null)
  const firstUserMsgRef = useRef(null)

  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, 50)
  }, [])

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isLoading) return

    if (!firstUserMsgRef.current) {
      firstUserMsgRef.current = text.trim()
    }

    const userMessage = {
      id:      Date.now(),
      role:    'user',
      content: text.trim(),
      ts:      new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)
    scrollToBottom()

    try {
      const data = await sendChatMessage(text.trim(), sessionId)

      const resolvedSessionId = sessionId || data.session_id
      if (!sessionId && data.session_id) {
        setSessionId(data.session_id)
      }

      const aiMessage = {
        id:      Date.now() + 1,
        role:    'assistant',
        content: data.answer,
        ts:      new Date(),

        // Terms glossary — array from backend, empty array if absent
        terms: data.terms_explained || [],

        meta: {
          intent:     data.intent,
          platform:   data.platform_detected,
          confidence: data.confidence,
          model:      data.model,
          tokens:     data.tokens_used,
          kpiFetched: data.kpi_data_fetched,
          ragFetched: data.rag_context_retrieved,
          recCount:   data.recommendations_count,
          turnCount:  data.conversation_length,
          termsCount: data.terms_count || 0,
        },
      }

      setMessages(prev => [...prev, aiMessage])
      setLastMeta(aiMessage.meta)
      scrollToBottom()

      if (onExchange && resolvedSessionId) {
        onExchange(resolvedSessionId, firstUserMsgRef.current, data.answer)
      }

    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Unknown error'
      setError(`Request failed: ${detail}`)
      setMessages(prev => [...prev, {
        id:      Date.now() + 2,
        role:    'error',
        content: `Something went wrong: ${detail}`,
        ts:      new Date(),
      }])
      scrollToBottom()
    } finally {
      setIsLoading(false)
    }
  }, [isLoading, sessionId, scrollToBottom, onExchange])

  const clearConversation = useCallback(async () => {
    if (sessionId) {
      try { await clearSession(sessionId) } catch (_) {}
    }
    setMessages([])
    setSessionId(null)
    setLastMeta(null)
    setError(null)
    firstUserMsgRef.current = null
  }, [sessionId])

  const loadSession = useCallback((entry) => {
    setMessages([{
      id:      Date.now(),
      role:    'assistant',
      content: `Resuming: **"${entry.title}"**\n\nType your next question to continue this conversation.`,
      ts:      new Date(),
      terms:   [],
      meta:    null,
    }])
    setSessionId(entry.id)
    setLastMeta(null)
    setError(null)
    firstUserMsgRef.current = entry.title
  }, [])

  return {
    messages,
    sessionId,
    isLoading,
    error,
    lastMeta,
    bottomRef,
    sendMessage,
    clearConversation,
    loadSession,
  }
}