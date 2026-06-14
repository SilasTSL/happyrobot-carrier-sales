import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { OUTCOME_COLORS } from '../ui/Badge'

const LABELS = {
  booked: 'Booked',
  not_eligible: 'Not Eligible',
  no_match: 'No Match',
  rate_not_agreed: 'Rate Not Agreed',
  hung_up: 'Hung Up',
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const { name, value, payload: d } = payload[0]
  return (
    <div className="bg-white border border-slate-200 rounded-lg shadow-lg p-3 text-sm">
      <p className="font-medium text-slate-700">{LABELS[name] ?? name}</p>
      <p className="tabular-nums text-slate-600">{value} calls ({d.pct?.toFixed(1)}%)</p>
    </div>
  )
}

export default function OutcomeDonut({ data }) {
  const chartData = (data ?? []).map(d => ({
    name: d.outcome,
    value: d.count,
    pct: d.pct,
  }))

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <p className="text-sm font-semibold text-slate-800 mb-2">Outcome Distribution</p>
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="45%"
            innerRadius={60}
            outerRadius={90}
            dataKey="value"
            nameKey="name"
            paddingAngle={2}
          >
            {chartData.map(entry => (
              <Cell key={entry.name} fill={OUTCOME_COLORS[entry.name] ?? '#94a3b8'} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            formatter={v => <span style={{ fontSize: 12, color: '#475569' }}>{LABELS[v] ?? v}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
