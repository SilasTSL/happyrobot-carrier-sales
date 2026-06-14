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
                <div className="w-7 h-7 bg-indigo-600 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
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
