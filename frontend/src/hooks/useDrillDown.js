/**
 * useDrillDown.js
 *
 * Manages the drill-down panel state.
 * When a user clicks a KPI card or chart, this hook opens
 * a slide-in panel with detailed data for that item.
 *
 * Usage:
 *   const { panel, openPanel, closePanel } = useDrillDown()
 *   openPanel({ type: 'platform', id: 'YouTube', data: {...} })
 */

import { useState, useCallback } from 'react'

export function useDrillDown() {
  const [panel, setPanel] = useState(null) // null = closed

  const openPanel = useCallback((config) => {
    // config = { type, title, subtitle, data, chartType }
    setPanel(config)
  }, [])

  const closePanel = useCallback(() => {
    setPanel(null)
  }, [])

  return { panel, openPanel, closePanel }
}