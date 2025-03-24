
// src/api/data.ts
import api from './config'
import type {
  EnvironmentalMeasurement,
  Prediction,
  Alert,
  UserAlert,
  DashboardData,
  MeasurementFilters,
  PredictionFilters,
  AlertFilters,
  PaginatedResponse
} from '@/types'

export const dataApi = {
  // Dashboard
  getDashboardData: (location?: string) => {
    return api.get<DashboardData>('/dashboard/', {
      params: location ? { location } : {}
    })
  },
  
  // Measurements
  getMeasurements: (filters?: MeasurementFilters) => {
    return api.get<PaginatedResponse<EnvironmentalMeasurement>>('/measurements/', {
      params: filters
    })
  },
  
  getMeasurement: (id: number) => {
    return api.get<EnvironmentalMeasurement>(`/measurements/${id}/`)
  },
  
  createMeasurement: (data: Partial<EnvironmentalMeasurement>) => {
    return api.post<EnvironmentalMeasurement>('/measurements/', data)
  },
  
  updateMeasurement: (id: number, data: Partial<EnvironmentalMeasurement>) => {
    return api.put<EnvironmentalMeasurement>(`/measurements/${id}/`, data)
  },
  
  deleteMeasurement: (id: number) => {
    return api.delete(`/measurements/${id}/`)
  },
  
  // Predictions
  getPredictions: (filters?: PredictionFilters) => {
    return api.get<PaginatedResponse<Prediction>>('/predictions/', {
      params: filters
    })
  },
  
  getPrediction: (id: number) => {
    return api.get<Prediction>(`/predictions/${id}/`)
  },
  
  createPrediction: (data: Partial<Prediction>) => {
    return api.post<Prediction>('/predictions/', data)
  },
  
  updatePrediction: (id: number, data: Partial<Prediction>) => {
    return api.put<Prediction>(`/predictions/${id}/`, data)
  },
  
  deletePrediction: (id: number) => {
    return api.delete(`/predictions/${id}/`)
  },
  
  // Alerts
  getAlerts: (filters?: AlertFilters) => {
    return api.get<PaginatedResponse<Alert>>('/alerts/', {
      params: filters
    })
  },
  
  getAlert: (id: number) => {
    return api.get<Alert>(`/alerts/${id}/`)
  },
  
  createAlert: (data: Partial<Alert>) => {
    return api.post<Alert>('/alerts/', data)
  },
  
  updateAlert: (id: number, data: Partial<Alert>) => {
    return api.put<Alert>(`/alerts/${id}/`, data)
  },
  
  deleteAlert: (id: number) => {
    return api.delete(`/alerts/${id}/`)
  },
  
  // User Alerts
  getUserAlerts: () => {
    return api.get<PaginatedResponse<UserAlert>>('/user-alerts/')
  },
  
  getUserAlert: (id: number) => {
    return api.get<UserAlert>(`/user-alerts/${id}/`)
  },
  
  markAlertAsRead: (id: number) => {
    return api.post<UserAlert>(`/user-alerts/${id}/mark_as_read/`)
  },
  
  markAllAlertsAsRead: () => {
    return api.post('/user-alerts/mark_all_as_read/')
  }
}