import React from 'react'

export default function PageHeader({
  title,
  subtitle,
  actions,
  className = '',
}: {
  title: React.ReactNode
  subtitle?: React.ReactNode
  actions?: React.ReactNode
  className?: string
}) {
  return (
    <div className={`mb-4 flex items-start justify-between gap-4 ${className}`}>
      <div>
        <h2 className="text-2xl font-semibold leading-tight">{title}</h2>
        {subtitle ? <div className="text-sm text-gray-600 mt-1">{subtitle}</div> : null}
      </div>
      {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
    </div>
  )
}
