export function Skeleton({ className = '' }) {
  return <div className={`animate-pulse bg-slate-200 rounded ${className}`} />
}

export function KpiSkeleton() {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-3">
      <Skeleton className="h-4 w-28" />
      <Skeleton className="h-8 w-20" />
      <Skeleton className="h-3 w-16" />
    </div>
  )
}

export function ChartSkeleton({ height = 'h-64' }) {
  return (
    <div className={`bg-white rounded-xl border border-slate-200 p-6 ${height}`}>
      <Skeleton className="h-4 w-32 mb-4" />
      <Skeleton className="h-full" />
    </div>
  )
}
