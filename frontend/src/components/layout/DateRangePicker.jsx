import { useState } from 'react'

const PRESETS = [
  { label: '7d', days: 7 },
  { label: '30d', days: 30 },
  { label: '60d', days: 60 },
]

function makeRange(days) {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - days)
  return { start, end }
}

export default function DateRangePicker({ onChange }) {
  const [active, setActive] = useState(30)

  function apply(days) {
    setActive(days)
    onChange(makeRange(days))
  }

  return (
    <div className="flex items-center gap-1">
      {PRESETS.map(p => (
        <button
          key={p.days}
          onClick={() => apply(p.days)}
          className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
            active === p.days
              ? 'bg-indigo-600 text-white'
              : 'text-slate-600 border border-slate-200 bg-white hover:bg-slate-50'
          }`}
        >
          {p.label}
        </button>
      ))}
    </div>
  )
}
