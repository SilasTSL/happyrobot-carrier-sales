function DeltaBadge({ delta_pct }) {
  if (delta_pct == null) return null
  const up = delta_pct >= 0
  return (
    <span className={`text-xs font-semibold flex items-center gap-0.5 ${up ? 'text-emerald-600' : 'text-rose-600'}`}>
      {up ? '↑' : '↓'} {Math.abs(delta_pct).toFixed(1)}%
    </span>
  )
}

export default function KpiCard({ label, value, kpi, subtext, higherIsBetter = true }) {
  const delta = kpi?.delta_pct
  const displayDelta = delta != null
    ? (higherIsBetter ? delta : -delta) >= 0
      ? delta
      : delta
    : null

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 flex flex-col gap-1">
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide leading-none">{label}</p>
      <p className="text-3xl font-bold tabular-nums text-slate-900 leading-tight">{value}</p>
      <div className="flex items-center gap-2 mt-0.5">
        {delta != null && <DeltaBadge delta_pct={higherIsBetter ? delta : delta != null ? -delta : null} />}
        {subtext && <span className="text-xs text-slate-400">{subtext}</span>}
      </div>
    </div>
  )
}
