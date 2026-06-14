import { createContext, useContext, useState } from 'react'
import api from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [company, setCompany] = useState(() => {
    const saved = sessionStorage.getItem('auth_company')
    return saved ? JSON.parse(saved) : null
  })

  async function login(username, password) {
    const { data } = await api.post('/auth/login', { username, password })
    sessionStorage.setItem('auth_token', data.access_token)
    sessionStorage.setItem('auth_company', JSON.stringify({ name: data.company_name, id: data.company_id }))
    setCompany({ name: data.company_name, id: data.company_id })
    return data
  }

  function logout() {
    sessionStorage.removeItem('auth_token')
    sessionStorage.removeItem('auth_company')
    setCompany(null)
  }

  return (
    <AuthContext.Provider value={{ company, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
