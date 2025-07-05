import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => config,
  error => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  response => response,
  async error => {
    const authStore = useAuthStore()
    
    if (error.response?.status === 401 && authStore.isAuthenticated) {
      // Try to refresh token
      const refreshed = await authStore.refreshAccessToken()
      
      if (refreshed) {
        // Retry original request
        error.config.headers['Authorization'] = `Bearer ${authStore.token}`
        return api.request(error.config)
      }
    }
    
    return Promise.reject(error)
  }
)

export default api