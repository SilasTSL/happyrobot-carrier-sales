import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = sessionStorage.getItem('auth_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      sessionStorage.removeItem('auth_token')
      sessionStorage.removeItem('auth_company')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
