import {
  Bar, BarChart, CartesianGrid, Line, ComposedChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-sm">
      <p className="font-medium text-slate-700 mb-1">{label} round{label !== '1' ? 's' : ''}</p>
      {payload.map(p => (
        <p key={p.dataKey} style={{ color: p.color }} className="tabular-nums">
          {p.name}: <span className="font-semibold">{p.dataKey === 'booking_rate' ? `${p.value?.toFixed(1)}%` : p.value}</span>
        </p>
      ))}
    </div>
  )
}

export default function NegotiationHistogram({ data }) {
  const chartData = (data ?? []).map(d => ({
    ...d,
    label: String(d.rounds),
  }))

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <p className="text-sm font-semibold text-slate-800 mb-4">Negotiation Rounds</p>
      <ResponsiveContainer width="100%" height={220}>
        <ComposedChart data={chartData} margin={{ top: 4, right: 24, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#64748b' }} tickLine={false} axisLine={false} label={{ value: 'rounds', position: 'insideBottom', offset: 0, fontSize: 11, fill: '#94a3b8' }} />
          <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#94a3b8' }} tickLine={false} axisLine={false} allowDecimals={false} />
          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11, fill: '#94a3b8' }} tickLine={false} axisLine={false} unit="%" domain={[0, 100]} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
          <Bar yAxisId="left" dataKey="count" name="Calls" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={50} />
          <Line yAxisId="right" type="monotone" dataKey="booking_rate" name="Booking Rate %" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981', r: 4 }} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
