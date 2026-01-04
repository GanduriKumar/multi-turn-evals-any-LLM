import React from 'react'

type Tone = 'neutral' | 'success' | 'warning' | 'danger' | 'info'

function toneClasses(tone: Tone) {
  switch (tone) {
    case 'success':
      return 'bg-green-100 text-green-700'
    case 'warning':
      return 'bg-yellow-100 text-yellow-700'
    case 'danger':
      return 'bg-red-100 text-red-700'
    case 'info':
      return 'bg-brand-50 text-brand-700'
    default:
      return 'bg-gray-100 text-gray-700'
  }
}

export default function Badge({ children, className = '', tone = 'neutral' }: { children: React.ReactNode; className?: string; tone?: Tone }) {
  return <span className={`text-xs px-2 py-1 rounded-md ${toneClasses(tone)} ${className}`}>{children}</span>
}
