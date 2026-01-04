import React from 'react'
import { NavLink } from 'react-router-dom'

function itemCls({ isActive }: { isActive: boolean }) {
  return (
    'flex items-center gap-2 px-3 py-2 rounded transition-colors ' +
    (isActive ? 'bg-blue-600 text-white' : 'text-gray-800 hover:bg-gray-100')
  )
}

const items = [
  { to: '/datasets', label: 'Datasets', icon: '📚' },
  { to: '/run-setup', label: 'Run Setup', icon: '⚙️' },
  { to: '/dashboard/example', label: 'Dashboard', icon: '📊' },
  { to: '/metrics/example', label: 'Metrics', icon: '📈' },
  { to: '/compare?baseline=&current=', label: 'Compare', icon: '🔀' },
  { to: '/viewer', label: 'Run Viewer', icon: '🗂️' },
]

export default function Sidebar() {
  return (
    <aside className="border-r min-h-screen p-4 bg-white">
      <div className="font-bold text-xl mb-6">Evaluator</div>
      <nav className="flex flex-col gap-1">
        {items.map((it) => (
          <NavLink key={it.to} to={it.to} className={itemCls} end={false}>
            <span aria-hidden>{it.icon}</span>
            <span>{it.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
