import { pct } from '../../lib/format'

export default function TopLanesTable({ data }) {
  const rows = data ?? []

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <p className="text-sm font-semibold text-slate-800 mb-4">Top Lanes by Volume</p>
      {rows.length === 0 ? (
        <p className="text-sm text-slate-400 text-center py-8">No lane data for this period</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left pb-2 text-xs font-medium text-slate-500 pr-3">Lane</th>
                <th className="text-center pb-2 text-xs font-medium text-slate-500 w-12">Equip.</th>
                <th className="text-right pb-2 text-xs font-medium text-slate-500 w-14">Calls</th>
                <th className="text-right pb-2 text-xs font-medium text-slate-500 w-20">Book Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {rows.map((r, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="py-2 pr-3 font-medium text-slate-800 text-xs leading-tight">
                    <span>{r.origin}</span>
                    <span className="text-slate-400 mx-1">→</span>
                    <span>{r.destination}</span>
                  </td>
                  <td className="py-2 text-center text-xs text-slate-500">{r.equipment_type?.split(' ')[0]}</td>
                  <td className="py-2 text-right tabular-nums text-slate-700">{r.calls}</td>
                  <td className="py-2 text-right">
                    <span className={`tabular-nums text-xs font-semibold ${r.booking_rate >= 50 ? 'text-emerald-600' : r.booking_rate >= 30 ? 'text-amber-600' : 'text-rose-600'}`}>
                      {pct(r.booking_rate)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
