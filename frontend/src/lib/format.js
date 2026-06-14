export const currency = v =>
  v == null ? '—' : `$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`

export const pct = (v, places = 1) =>
  v == null ? '—' : `${Number(v).toFixed(places)}%`

export const num = v =>
  v == null ? '—' : Number(v).toLocaleString('en-US')

export const decimal = (v, places = 2) =>
  v == null ? '—' : Number(v).toFixed(places)

export const shortDate = iso => {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export const fullDatetime = iso => {
  if (!iso) return '—'
  return new Date(iso + 'Z').toLocaleString('en-US', {
    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true
  })
}
