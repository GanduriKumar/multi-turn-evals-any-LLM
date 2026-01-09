import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

type SettingsResp = {
  industry_vertical?: string
  supported_verticals?: string[]
}

type VerticalContextType = {
  vertical: string
  supported: string[]
  setVertical: (v: string) => Promise<void>
  loading: boolean
}

const VerticalContext = createContext<VerticalContextType | null>(null)

export function VerticalProvider({ children }: { children: React.ReactNode }) {
  const [vertical, setVerticalState] = useState<string>('commerce')
  const [supported, setSupported] = useState<string[]>([ 'commerce', 'banking', 'finance', 'healthcare' ])
  const [loading, setLoading] = useState(true)

  const load = async () => {
    try {
      const r = await fetch('/settings')
      const js: SettingsResp = await r.json()
      if (Array.isArray(js.supported_verticals)) setSupported(js.supported_verticals)
      if (typeof js.industry_vertical === 'string' && js.industry_vertical) setVerticalState(js.industry_vertical)
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const setVertical = async (v: string) => {
    if (!v) return
    try {
      await fetch('/settings', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ industry_vertical: v }) })
      setVerticalState(v)
    } catch {}
  }

  const value = useMemo(() => ({ vertical, supported, setVertical, loading }), [vertical, supported, loading])
  return <VerticalContext.Provider value={value}>{children}</VerticalContext.Provider>
}

export function useVertical() {
  const ctx = useContext(VerticalContext)
  if (!ctx) throw new Error('useVertical must be used within VerticalProvider')
  return ctx
}
