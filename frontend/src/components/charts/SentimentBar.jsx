import {
  Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts'
import { SENTIMENT_COLORS } from '../ui/Badge'

const LABELS = { positive: 'Positive', neutral: 'Neutral', negative: 'Negative' }

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-sm">
      <p className="font-medium text-slate-700">{LABELS[d.sentiment] ?? d.sentiment}</p>
      <p className="text-slate-600">{d.count} calls</p>
      <p className="text-slate-600">Booking rate: <span className="font-semibold">{d.booking_rate?.toFixed(1)}%</span></p>
    </div>
  )
}

export default function SentimentBar({ data }) {
  const chartData = (data ?? []).map(d => ({
    ...d,
    label: LABELS[d.sentiment] ?? d.sentiment,
  }))

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <p className="text-sm font-semibold text-slate-800 mb-4">Sentiment vs. Booking Rate</p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData} margin={{ top: 16, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#64748b' }} tickLine={false} axisLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} tickLine={false} axisLine={false} allowDecimals={false} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" radius={[4, 4, 0, 0]} maxBarSize={60}>
            {chartData.map(d => (
              <Cell key={d.sentiment} fill={SENTIMENT_COLORS[d.sentiment] ?? '#94a3b8'} />
            ))}
            <LabelList dataKey="booking_rate" position="top" formatter={v => `${v?.toFixed(0)}% booked`} style={{ fontSize: 10, fill: '#64748b' }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
