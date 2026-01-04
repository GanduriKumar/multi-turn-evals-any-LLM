import React from 'react'

export type Segment = { label: string; value: number; color: 'blue'|'green'|'yellow'|'red' }

function colorClass(color: Segment['color']) {
  return (
    {
      blue: 'bg-google-blue',
      green: 'bg-google-green',
      yellow: 'bg-google-yellow',
      red: 'bg-google-red',
    }[color] || 'bg-slate-300'
  )
}

export default function StatusMeter({ segments, showLegend = true }: { segments: Segment[]; showLegend?: boolean }) {
  const total = segments.reduce((a, s) => a + s.value, 0) || 1
  return (
    <div>
      <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden flex">
        {segments.map((s, i) => (
          <div key={i} className={colorClass(s.color)} style={{ width: `${Math.max(0, Math.min(100, (s.value / total) * 100))}%` }} />
        ))}
      </div>
      {showLegend && (
        <div className="flex justify-between text-xs text-slate-600 mt-1">
          {segments.map((s, i) => (
            <div key={i} className="flex items-center gap-1">
              <span className={`inline-block w-2 h-2 rounded-full ${colorClass(s.color)}`} />
              <span>{s.label}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
