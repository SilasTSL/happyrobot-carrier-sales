import { pct } from '../../lib/format'

function GaugeBar({ value, max = 100, color }) {
  const pctVal = Math.min(Math.max(value ?? 0, 0), max)
  const width = `${(pctVal / max) * 100}%`
  return (
    <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
      <div
        className="h-3 rounded-full transition-all duration-500"
        style={{ width, backgroundColor: color }}
      />
    </div>
  )
}

function colorFor(v) {
  if (v == null) return '#94a3b8'
  if (v < 40) return '#10b981'   // green — low headroom used = margin preserved
  if (v < 70) return '#f59e0b'   // amber
  return '#f43f5e'               // red — high headroom = margin at risk
}

export default function MarginGauge({ summary }) {
  const headroom = summary?.avg_margin_headroom_used?.value
  const delta = summary?.avg_margin_headroom_used?.value
  const atMax = summary?.calls_at_max_rate?.value
  const atMaxPct = summary?.calls_at_max_rate_pct?.value
  const rateDelta = summary?.avg_rate_delta?.value

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <p className="text-sm font-semibold text-slate-800 mb-4">Margin Intelligence</p>
      <div className="space-y-5">
        <div>
          <div className="flex justify-between items-baseline mb-1.5">
            <span className="text-xs text-slate-500">Avg. margin headroom used</span>
            <span className="text-sm font-bold tabular-nums text-slate-800">{pct(headroom)}</span>
          </div>
          <GaugeBar value={headroom} color={colorFor(headroom)} />
          <p className="text-xs text-slate-400 mt-1">
            How far toward the loadboard ceiling the agent conceded. Lower = more margin retained.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-100">
          <div>
            <p className="text-xs text-slate-500 mb-0.5">Avg. rate concession</p>
            <p className={`text-xl font-bold tabular-nums ${rateDelta == null ? 'text-slate-900' : rateDelta <= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {rateDelta != null ? `${rateDelta < 0 ? '-' : '+'}$${Math.abs(rateDelta).toFixed(0)}` : '—'}
            </p>
            <p className="text-xs text-slate-400">vs. loadboard rate</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-0.5">At max rate</p>
            <p className="text-xl font-bold tabular-nums text-rose-600">
              {atMax ?? '—'}
              <span className="text-sm font-medium text-slate-400 ml-1">
                ({pct(atMaxPct)})
              </span>
            </p>
            <p className="text-xs text-slate-400">loads booked at ceiling</p>
          </div>
        </div>
      </div>
    </div>
  )
}
