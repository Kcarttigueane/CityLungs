// src/api/auth.ts
import api from './config'
import type {
  LoginCredentials,
  RegistrationData,
  AuthResponse,
  User,
  PasswordChangeData,
  PasswordResetRequestData,
  PasswordResetConfirmData
} from '@/types'

export const authApi = {
  // Register a new user
  register: (data: RegistrationData) => {
    return api.post<User>('/auth/register/', data)
  },
  
  // Login user
  login: (credentials: LoginCredentials) => {
    return api.post<AuthResponse>('/auth/login/', credentials)
  },
  
  // Logout user
  logout: (refreshToken: string) => {
    return api.post('/auth/logout/', { refresh: refreshToken })
  },
  
  // Refresh token
  refreshToken: (refreshToken: string) => {
    return api.post<{ access: string }>('/auth/token/refresh/', {
      refresh: refreshToken
    })
  },
  
  // Get user profile
  getProfile: () => {
    return api.get<User>('/auth/user/profile/')
  },
  
  // Update user profile
  updateProfile: (data: Partial<User>) => {
    return api.put<User>('/auth/user/profile/', data)
  },
  
  // Change password
  changePassword: (data: PasswordChangeData) => {
    return api.post('/auth/user/password/change/', data)
  },
  
  // Request password reset
  requestPasswordReset: (data: PasswordResetRequestData) => {
    return api.post('/auth/user/password/reset/request/', data)
  },
  
  // Confirm password reset
  confirmPasswordReset: (data: PasswordResetConfirmData) => {
    return api.post('/auth/user/password/reset/confirm/', data)
  }
}