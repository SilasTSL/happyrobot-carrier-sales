import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import AppShell from './components/layout/AppShell'
import LoginPage from './pages/LoginPage'
import OverviewPage from './pages/OverviewPage'
import CallLogPage from './pages/CallLogPage'

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 0, retry: 1 } },
})

function ProtectedRoute({ children }) {
  const { company } = useAuth()
  return company ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppShell />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/overview" replace />} />
              <Route path="overview" element={<OverviewPage />} />
              <Route path="calls" element={<CallLogPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}
