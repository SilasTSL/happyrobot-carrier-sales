import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  flexRender, getCoreRowModel, useReactTable,
} from '@tanstack/react-table'
import { keepPreviousData } from '@tanstack/react-query'
import { useDateRange } from '../components/layout/AppShell'
import { OutcomeBadge, SentimentBadge } from '../components/ui/Badge'
import { ChartSkeleton } from '../components/ui/Skeleton'
import { currency, fullDatetime } from '../lib/format'
import api from '../lib/api'

const OUTCOMES = ['booked', 'not_eligible', 'no_match', 'rate_not_agreed', 'hung_up']
const SENTIMENTS = ['positive', 'neutral', 'negative']

function startParam(dateRange) {
  if (!dateRange) return {}
  return { start: dateRange.start.toISOString() }
}

function exportCsv(rows) {
  const headers = ['Timestamp', 'Carrier', 'MC#', 'Origin', 'Destination', 'Equip.', 'Outcome', 'Sentiment', 'Loadboard Rate', 'Final Rate', 'Max Rate', 'Neg. Rounds']
  const lines = rows.map(r => [
    r.timestamp, r.carrier_name ?? '', r.mc_number ?? '',
    r.origin ?? '', r.destination ?? '', r.equipment_type ?? '',
    r.outcome, r.sentiment,
    r.loadboard_rate ?? '', r.final_rate ?? '', r.max_rate ?? '',
    r.negotiation_rounds,
  ].map(v => `"${v}"`).join(','))
  const csv = [headers.join(','), ...lines].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'calls.csv'; a.click()
  URL.revokeObjectURL(url)
}

function DetailDrawer({ call, onClose }) {
  if (!call) return null
  const rows = [
    ['Call ID', call.call_id],
    ['Timestamp', fullDatetime(call.timestamp)],
    ['Carrier', call.carrier_name ?? '—'],
    ['MC Number', call.mc_number ?? '—'],
    ['Lane', call.origin && call.destination ? `${call.origin} → ${call.destination}` : '—'],
    ['Equipment', call.equipment_type ?? '—'],
    ['Outcome', <OutcomeBadge key="o" value={call.outcome} />],
    ['Sentiment', <SentimentBadge key="s" value={call.sentiment} />],
    ['Loadboard Rate', currency(call.loadboard_rate)],
    ['Final Rate', currency(call.final_rate)],
    ['Max Rate', currency(call.max_rate)],
    ['Negotiation Rounds', call.negotiation_rounds],
  ]
  return (
    <div className="fixed inset-0 z-50 flex" onClick={onClose}>
      <div className="flex-1" />
      <div
        className="w-80 bg-white shadow-2xl border-l border-slate-200 overflow-y-auto"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <p className="text-sm font-semibold text-slate-900">Call Details</p>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-lg leading-none">✕</button>
        </div>
        <dl className="divide-y divide-slate-100">
          {rows.map(([k, v]) => (
            <div key={k} className="px-5 py-3 flex flex-col gap-0.5">
              <dt className="text-xs text-slate-500 font-medium">{k}</dt>
              <dd className="text-sm text-slate-800 font-medium">{v}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  )
}

const COLUMNS = [
  {
    accessorKey: 'timestamp',
    header: 'Time',
    cell: ({ getValue }) => <span className="text-xs text-slate-600 tabular-nums">{fullDatetime(getValue())}</span>,
    size: 140,
  },
  {
    accessorKey: 'carrier_name',
    header: 'Carrier',
    cell: ({ getValue }) => <span className="text-sm text-slate-800 font-medium">{getValue() ?? <span className="text-slate-400">—</span>}</span>,
  },
  {
    accessorKey: 'mc_number',
    header: 'MC#',
    cell: ({ getValue }) => <span className="text-xs text-slate-500 font-mono">{getValue()?.replace(/^MC\s*/i, '') ?? '—'}</span>,
    size: 100,
  },
  {
    id: 'lane',
    header: 'Lane',
    accessorFn: row => row.origin && row.destination ? `${row.origin} → ${row.destination}` : null,
    cell: ({ getValue }) => <span className="text-xs text-slate-600">{getValue() ?? <span className="text-slate-400">—</span>}</span>,
  },
  {
    accessorKey: 'outcome',
    header: 'Outcome',
    cell: ({ getValue }) => <OutcomeBadge value={getValue()} />,
    size: 130,
  },
  {
    accessorKey: 'sentiment',
    header: 'Sentiment',
    cell: ({ getValue }) => <SentimentBadge value={getValue()} />,
    size: 90,
  },
  {
    accessorKey: 'loadboard_rate',
    header: 'Board',
    cell: ({ getValue }) => <span className="text-xs tabular-nums text-slate-500">{currency(getValue())}</span>,
    size: 80,
  },
  {
    accessorKey: 'final_rate',
    header: 'Final',
    cell: ({ getValue }) => <span className="text-sm tabular-nums font-semibold text-slate-900">{currency(getValue())}</span>,
    size: 80,
  },
  {
    accessorKey: 'negotiation_rounds',
    header: 'Rounds',
    cell: ({ getValue }) => <span className="text-xs tabular-nums text-slate-500 text-center block">{getValue()}</span>,
    size: 60,
  },
]

export default function CallLogPage() {
  const { dateRange } = useDateRange()
  const params = startParam(dateRange)

  const [page, setPage] = useState(1)
  const [outcome, setOutcome] = useState('')
  const [sentiment, setSentiment] = useState('')
  const [sort, setSort] = useState('timestamp_desc')
  const [selectedCall, setSelectedCall] = useState(null)

  const queryParams = {
    ...params,
    page,
    limit: 50,
    sort,
    ...(outcome ? { outcome } : {}),
    ...(sentiment ? { sentiment } : {}),
  }

  const { data, isPending, isError, error } = useQuery({
    queryKey: ['calls', queryParams],
    queryFn: () => api.get('/calls', { params: { ...queryParams, end: new Date().toISOString() } }).then(r => r.data),
    placeholderData: keepPreviousData,
  })

  function resetFilters() {
    setOutcome(''); setSentiment(''); setPage(1)
  }

  const table = useReactTable({
    data: data?.data ?? [],
    columns: COLUMNS,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
    pageCount: data ? Math.ceil(data.total / 50) : 0,
  })

  const totalPages = data ? Math.ceil(data.total / 50) : 1

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-lg font-bold text-slate-900">Call Log</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {data ? `${data.total.toLocaleString()} calls` : '—'} in period
          </p>
        </div>
        <button
          onClick={() => data?.data?.length && exportCsv(data.data)}
          disabled={!data?.data?.length}
          className="flex items-center gap-1.5 text-xs font-semibold text-indigo-600 border border-indigo-200 bg-indigo-50 hover:bg-indigo-100 rounded-lg px-3 py-2 transition disabled:opacity-40"
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2 bg-white border border-slate-200 rounded-xl p-3">
        <select
          value={outcome}
          onChange={e => { setOutcome(e.target.value); setPage(1) }}
          className="text-xs text-slate-700 border border-slate-200 rounded-md px-2.5 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
        >
          <option value="">All outcomes</option>
          {OUTCOMES.map(o => <option key={o} value={o}>{o.replace(/_/g, ' ')}</option>)}
        </select>
        <select
          value={sentiment}
          onChange={e => { setSentiment(e.target.value); setPage(1) }}
          className="text-xs text-slate-700 border border-slate-200 rounded-md px-2.5 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
        >
          <option value="">All sentiments</option>
          {SENTIMENTS.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select
          value={sort}
          onChange={e => { setSort(e.target.value); setPage(1) }}
          className="text-xs text-slate-700 border border-slate-200 rounded-md px-2.5 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
        >
          <option value="timestamp_desc">Newest first</option>
          <option value="timestamp_asc">Oldest first</option>
          <option value="final_rate_desc">Rate: high to low</option>
          <option value="final_rate_asc">Rate: low to high</option>
        </select>
        {(outcome || sentiment) && (
          <button onClick={resetFilters} className="text-xs text-slate-500 hover:text-slate-700 underline">Clear filters</button>
        )}
      </div>

      {/* Table */}
      {isPending ? (
        <ChartSkeleton height="h-96" />
      ) : isError ? (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-sm text-rose-700">
          Failed to load calls — {error?.message}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                {table.getHeaderGroups().map(hg => (
                  <tr key={hg.id} className="border-b border-slate-100 bg-slate-50">
                    {hg.headers.map(header => (
                      <th key={header.id} className="text-left px-4 py-2.5 text-xs font-semibold text-slate-500 whitespace-nowrap" style={{ width: header.getSize() }}>
                        {flexRender(header.column.columnDef.header, header.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody className="divide-y divide-slate-50">
                {table.getRowModel().rows.length === 0 ? (
                  <tr>
                    <td colSpan={COLUMNS.length} className="text-center py-12 text-sm text-slate-400">
                      No calls match the current filters
                    </td>
                  </tr>
                ) : (
                  table.getRowModel().rows.map(row => (
                    <tr
                      key={row.id}
                      onClick={() => setSelectedCall(row.original)}
                      className="hover:bg-slate-50 cursor-pointer transition-colors"
                    >
                      {row.getVisibleCells().map(cell => (
                        <td key={cell.id} className="px-4 py-2.5 whitespace-nowrap">
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100">
            <span className="text-xs text-slate-500">
              Page {page} of {totalPages} · {data?.total ?? 0} total
            </span>
            <div className="flex gap-1">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 text-xs font-medium text-slate-600 border border-slate-200 rounded-md hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                ← Prev
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="px-3 py-1.5 text-xs font-medium text-slate-600 border border-slate-200 rounded-md hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next →
              </button>
            </div>
          </div>
        </div>
      )}

      <DetailDrawer call={selectedCall} onClose={() => setSelectedCall(null)} />
    </div>
  )
}
