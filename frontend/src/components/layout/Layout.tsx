import React from 'react'
import NavBar from './NavBar'

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <NavBar />
      <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
    </div>
  )
}
