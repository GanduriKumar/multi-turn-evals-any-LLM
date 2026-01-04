import React from 'react'
import { Link, NavLink } from 'react-router-dom'

function navClass({ isActive }: { isActive: boolean }) {
  return 'px-2 py-1 rounded ' + (isActive ? 'bg-blue-600 text-white' : 'text-blue-600 hover:bg-blue-50')
}

export default function NavBar() {
  return (
    <header className="sticky top-0 z-20 bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60 border-b">
      <div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
        <Link to="/" className="text-2xl font-bold">Evaluator Workbench</Link>
        <nav className="flex gap-2">
          <NavLink to="/datasets" className={navClass}>Datasets</NavLink>
          <NavLink to="/run-setup" className={navClass}>Run Setup</NavLink>
          <NavLink to="/dashboard/example" className={navClass}>Dashboard</NavLink>
          <NavLink to="/metrics/example" className={navClass}>Metrics</NavLink>
          <NavLink to="/compare?baseline=&current=" className={navClass}>Compare</NavLink>
          <NavLink to="/viewer" className={navClass}>Run Viewer</NavLink>
        </nav>
      </div>
    </header>
  )
}
