import React from 'react'

export default function Card({ title, children }: { title: string, children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
      <div className="border-b border-gray-100 px-4 py-2 font-medium text-gray-800">{title}</div>
      <div className="p-4">{children}</div>
    </div>
  )
}
