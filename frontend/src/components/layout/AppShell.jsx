import { createContext, useContext, useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import DateRangePicker from './DateRangePicker'

function makeRange(days) {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - days)
  return { start, end }
}

const DateRangeContext = createContext(null)
export const useDateRange = () => useContext(DateRangeContext)

const navClass = ({ isActive }) =>
  `px-3 py-1.5 text-sm rounded-md font-medium transition-colors ${
    isActive
      ? 'bg-slate-100 text-slate-900'
      : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
  }`

export default function AppShell() {
  const { company, logout } = useAuth()
  const [dateRange, setDateRange] = useState(makeRange(30))

  return (
    <DateRangeContext.Provider value={{ dateRange, setDateRange }}>
      <div className="min-h-screen bg-slate-50">
        <header className="bg-white border-b border-slate-200 sticky top-0 z-20">
          <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between gap-4">
            {/* Brand + nav */}
            <div className="flex items-center gap-6 shrink-0">
              <div className="flex items-center gap-2">
                <img src="/favicon.svg" alt="HappyRobot" className="w-7 h-7" />
                <span className="font-semibold text-slate-900 text-sm">HappyRobot</span>
              </div>
              <nav className="flex gap-0.5">
                <NavLink to="/overview" className={navClass}>Overview</NavLink>
                <NavLink to="/calls" className={navClass}>Call Log</NavLink>
              </nav>
            </div>

            {/* Right controls */}
            <div className="flex items-center gap-4">
              <DateRangePicker onChange={setDateRange} />
              <div className="h-5 w-px bg-slate-200" />
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-xs text-slate-500 leading-none">Logged in as</p>
                  <p className="text-sm font-semibold text-slate-800 leading-none mt-0.5">{company?.name}</p>
                </div>
                <button
                  onClick={logout}
                  className="text-xs text-slate-500 hover:text-rose-600 transition-colors font-medium border border-slate-200 rounded-md px-2.5 py-1.5"
                >
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-6 py-6">
          <Outlet />
        </main>
      </div>
    </DateRangeContext.Provider>
  )
}
