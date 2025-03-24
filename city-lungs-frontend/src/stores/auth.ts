import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type {
  User,
  LoginCredentials,
  RegistrationData,
  AuthState,
  PasswordChangeData
} from '@/types'
import router from '@/router'
import { message } from 'ant-design-vue'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // Load saved auth state from localStorage
  const initializeAuth = () => {
    try {
      const savedUser = localStorage.getItem('user')
      const savedAccessToken = localStorage.getItem('accessToken')
      const savedRefreshToken = localStorage.getItem('refreshToken')
      
      if (savedUser) user.value = JSON.parse(savedUser)
      if (savedAccessToken) accessToken.value = savedAccessToken
      if (savedRefreshToken) refreshToken.value = savedRefreshToken
    } catch (err) {
      console.error('Failed to initialize auth state:', err)
    }
  }
  
  // Initialize on store creation
  initializeAuth()
  
  // Computed
  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isCitizen = computed(() => user.value?.role === 'citizen')
  
  // Actions
  const register = async (registerData: RegistrationData) => {
    isLoading.value = true
    error.value = null
    
    try {
      await authApi.register(registerData)
      message.success('Registration successful! Please log in.')
      router.push('/login')
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed'
      message.error(error.value)
      
      return false
    } finally {
      isLoading.value = false
    }
  }
  
  const login = async (credentials: LoginCredentials) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authApi.login(credentials)
      const { user: userData, access, refresh } = response.data
      
      // Save to state
      user.value = userData
      accessToken.value = access
      refreshToken.value = refresh
      
      // Save to localStorage
      localStorage.setItem('user', JSON.stringify(userData))
      localStorage.setItem('accessToken', access)
      localStorage.setItem('refreshToken', refresh)
      
      message.success(`Welcome, ${userData.first_name}!`)
      router.push('/')
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      message.error(error.value)
      
      return false
    } finally {
      isLoading.value = false
    }
  }
  
  const logout = async () => {
    isLoading.value = true
    
    try {
      if (refreshToken.value) {
        await authApi.logout(refreshToken.value)
      }
    } catch (err) {
      console.error('Error during logout:', err)
    } finally {
      // Clear state regardless of API success
      user.value = null
      accessToken.value = null
      refreshToken.value = null
      
      // Remove from localStorage
      localStorage.removeItem('user')
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      
      isLoading.value = false
      
      message.success('You have been logged out')
      router.push('/login')
    }
  }
  
  const refreshTokenAction = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }
    
    try {
      const response = await authApi.refreshToken(refreshToken.value)
      accessToken.value = response.data.access
      
      // Update localStorage
      localStorage.setItem('accessToken', response.data.access)
      
      return response.data.access
    } catch (err) {
      // Clear auth state on refresh failure
      logout()
      throw err
    }
  }
  
  const updateProfile = async (profileData: Partial<User>) => {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authApi.updateProfile(profileData)
      
      // Update user in state and localStorage
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      
      message.success('Profile updated successfully')
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update profile'
      message.error(error.value)
      return false
    } finally {
      isLoading.value = false
    }
  }
  
  const changePassword = async (passwordData: PasswordChangeData) => {
    isLoading.value = true
    error.value = null
    
    try {
      await authApi.changePassword(passwordData)
      message.success('Password changed successfully')
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to change password'
      message.error(error.value)
      return false
    } finally {
      isLoading.value = false
    }
  }
  
  // Return store properties and methods
  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    
    // Computed
    isAuthenticated,
    isAdmin,
    isCitizen,
    
    // Actions
    register,
    login,
    logout,
    refreshToken: refreshTokenAction,
    updateProfile,
    changePassword
  }
})