import { useQuery } from '@tanstack/react-query'
import { useDateRange } from '../components/layout/AppShell'
import KpiCard from '../components/kpi/KpiCard'
import CallsOverTime from '../components/charts/CallsOverTime'
import OutcomeDonut from '../components/charts/OutcomeDonut'
import SentimentBar from '../components/charts/SentimentBar'
import NegotiationHistogram from '../components/charts/NegotiationHistogram'
import MarginGauge from '../components/charts/MarginGauge'
import TopLanesTable from '../components/charts/TopLanesTable'
import { KpiSkeleton, ChartSkeleton } from '../components/ui/Skeleton'
import { currency, pct, num, decimal } from '../lib/format'
import api from '../lib/api'

function startParam(dateRange) {
  if (!dateRange) return {}
  return { start: dateRange.start.toISOString() }
}

function withNow(params) {
  return { ...params, end: new Date().toISOString() }
}

function ErrorBanner({ msg }) {
  return (
    <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-sm text-rose-700">
      Failed to load data — {msg ?? 'please try again.'}
    </div>
  )
}

export default function OverviewPage() {
  const { dateRange } = useDateRange()
  const params = startParam(dateRange)

  const summary = useQuery({
    queryKey: ['summary', params],
    queryFn: () => api.get('/metrics/summary', { params: withNow(params) }).then(r => r.data),
  })

  const timeseries = useQuery({
    queryKey: ['timeseries', params],
    queryFn: () => api.get('/metrics/timeseries', { params: { ...withNow(params), interval: 'day' } }).then(r => r.data),
  })

  const breakdowns = useQuery({
    queryKey: ['breakdowns', params],
    queryFn: () => api.get('/metrics/breakdowns', { params: withNow(params) }).then(r => r.data),
  })

  const s = summary.data
  const b = breakdowns.data
  const t = timeseries.data

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-bold text-slate-900">Overview</h1>
        <p className="text-sm text-slate-500 mt-0.5">Carrier call performance for the selected period</p>
      </div>

      {/* KPI row */}
      {summary.isError ? (
        <ErrorBanner msg={summary.error?.message} />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {summary.isPending ? (
            Array.from({ length: 5 }).map((_, i) => <KpiSkeleton key={i} />)
          ) : (
            <>
              <KpiCard
                label="Total Calls"
                value={num(s.total_calls.value)}
                kpi={s.total_calls}
                subtext="vs prior period"
              />
              <KpiCard
                label="Booking Rate"
                value={pct(s.booking_rate.value)}
                kpi={s.booking_rate}
                subtext="eligible calls"
              />
              <KpiCard
                label="Loads Booked"
                value={num(s.loads_booked.value)}
                kpi={s.loads_booked}
              />
              <KpiCard
                label="Committed Revenue"
                value={currency(s.total_committed_revenue.value)}
                kpi={s.total_committed_revenue}
                subtext="sum of final rates"
              />
              <KpiCard
                label="Avg. Rate Concession"
                value={s.avg_rate_delta.value != null
                  ? `${s.avg_rate_delta.value < 0 ? '-' : '+'}$${decimal(Math.abs(s.avg_rate_delta.value), 0)}`
                  : '—'}
                kpi={s.avg_rate_delta}
                subtext="vs. loadboard rate"
                higherIsBetter={false}
              />
            </>
          )}
        </div>
      )}

      {/* Secondary KPI strip */}
      {!summary.isPending && !summary.isError && s && (
        <div className="flex flex-wrap gap-3">
          {[
            { label: 'MC Eligibility', value: breakdowns.data ? `${(100 - breakdowns.data.outcomes.find(o => o.outcome === 'not_eligible')?.pct ?? 0).toFixed(1)}%` : '—' },
            { label: 'Avg Negotiation Rounds', value: decimal(s.avg_negotiation_rounds.value) },
            { label: 'Margin Headroom Used', value: pct(s.avg_margin_headroom_used.value) },
            { label: 'At Max Rate', value: `${num(s.calls_at_max_rate.value)} loads (${pct(s.calls_at_max_rate_pct.value)})` },
          ].map(item => (
            <div key={item.label} className="bg-white rounded-lg border border-slate-200 px-4 py-2.5 flex items-center gap-3">
              <span className="text-xs text-slate-500">{item.label}</span>
              <span className="text-sm font-bold tabular-nums text-slate-800">{item.value}</span>
            </div>
          ))}
        </div>
      )}

      {/* Charts grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {timeseries.isPending ? <ChartSkeleton height="h-72" /> : timeseries.isError ? <ErrorBanner /> : (
          <CallsOverTime data={t.data} />
        )}
        {breakdowns.isPending ? <ChartSkeleton height="h-72" /> : breakdowns.isError ? <ErrorBanner /> : (
          <OutcomeDonut data={b.outcomes} />
        )}
        {breakdowns.isPending ? <ChartSkeleton height="h-72" /> : breakdowns.isError ? <ErrorBanner /> : (
          <SentimentBar data={b.sentiments} />
        )}
        {breakdowns.isPending ? <ChartSkeleton height="h-72" /> : breakdowns.isError ? <ErrorBanner /> : (
          <NegotiationHistogram data={b.negotiation_rounds} />
        )}
        {summary.isPending ? <ChartSkeleton height="h-64" /> : summary.isError ? <ErrorBanner /> : (
          <MarginGauge summary={s} />
        )}
        {breakdowns.isPending ? <ChartSkeleton height="h-64" /> : breakdowns.isError ? <ErrorBanner /> : (
          <TopLanesTable data={b.top_lanes} />
        )}
      </div>
    </div>
  )
}
