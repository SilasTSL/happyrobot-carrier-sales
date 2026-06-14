const OUTCOME = {
  booked:          { label: 'Booked',          cls: 'bg-emerald-100 text-emerald-700' },
  not_eligible:    { label: 'Not Eligible',    cls: 'bg-rose-100 text-rose-700' },
  no_match:        { label: 'No Match',        cls: 'bg-amber-100 text-amber-700' },
  rate_not_agreed: { label: 'Rate Not Agreed', cls: 'bg-orange-100 text-orange-700' },
  hung_up:         { label: 'Hung Up',         cls: 'bg-slate-100 text-slate-600' },
}

const SENTIMENT = {
  positive: { label: 'Positive', cls: 'bg-emerald-100 text-emerald-700' },
  neutral:  { label: 'Neutral',  cls: 'bg-amber-100 text-amber-700' },
  negative: { label: 'Negative', cls: 'bg-rose-100 text-rose-700' },
}

export function OutcomeBadge({ value }) {
  const cfg = OUTCOME[value] ?? { label: value, cls: 'bg-slate-100 text-slate-600' }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${cfg.cls}`}>
      {cfg.label}
    </span>
  )
}

export function SentimentBadge({ value }) {
  const cfg = SENTIMENT[value] ?? { label: value, cls: 'bg-slate-100 text-slate-600' }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${cfg.cls}`}>
      {cfg.label}
    </span>
  )
}

export const OUTCOME_COLORS = {
  booked: '#10b981',
  not_eligible: '#f43f5e',
  no_match: '#f59e0b',
  rate_not_agreed: '#f97316',
  hung_up: '#94a3b8',
}

export const SENTIMENT_COLORS = {
  positive: '#10b981',
  neutral: '#f59e0b',
  negative: '#f43f5e',
}
