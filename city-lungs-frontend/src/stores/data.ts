/* eslint-disable @typescript-eslint/no-explicit-any */
// src/stores/data.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { dataApi } from '@/api/data'
import type {
  DashboardData,
  EnvironmentalMeasurement,
  Prediction,
  Alert,
  UserAlert,
  MeasurementFilters,
  PredictionFilters,
  AlertFilters,
} from '@/types'
import { message } from 'ant-design-vue'

export const useDataStore = defineStore('data', () => {
  // State
  const dashboardData = ref<DashboardData | null>(null)
  const measurements = ref<EnvironmentalMeasurement[]>([])
  const predictions = ref<Prediction[]>([])
  const alerts = ref<Alert[]>([])
  const userAlerts = ref<UserAlert[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const latestMeasurements = computed(() =>
    measurements.value
      .slice()
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, 10),
  )

  const upcomingPredictions = computed(() =>
    predictions.value
      .slice()
      .sort((a, b) => new Date(a.target_time).getTime() - new Date(b.target_time).getTime())
      .filter((p) => new Date(p.target_time) > new Date()),
  )

  const activeAlerts = computed(() => alerts.value.filter((alert) => alert.is_active))

  const unreadUserAlerts = computed(() =>
    userAlerts.value.filter((userAlert) => !userAlert.is_read),
  )

  // Actions
  const fetchDashboardData = async (location?: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await dataApi.getDashboardData(location)
      dashboardData.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch dashboard data'
      message.error(error.value)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const fetchMeasurements = async (filters?: MeasurementFilters) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await dataApi.getMeasurements(filters)
      measurements.value = response.data.results
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch measurements'
      message.error(error.value)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const fetchPredictions = async (filters?: PredictionFilters) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await dataApi.getPredictions(filters)
      predictions.value = response.data.results
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch predictions'
      message.error(error.value)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const fetchAlerts = async (filters?: AlertFilters) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await dataApi.getAlerts(filters)
      alerts.value = response.data.results
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch alerts'
      message.error(error.value)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const fetchUserAlerts = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await dataApi.getUserAlerts()
      userAlerts.value = response.data.results
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch user alerts'
      message.error(error.value)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const markAlertAsRead = async (id: number) => {
    try {
      await dataApi.markAlertAsRead(id)

      // Update the local state
      const index = userAlerts.value.findIndex((alert) => alert.id === id)
      if (index !== -1) {
        userAlerts.value[index].is_read = true
        userAlerts.value[index].read_at = new Date().toISOString()
      }

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to mark alert as read'
      message.error(error.value)
      return false
    }
  }

  const markAllAlertsAsRead = async () => {
    try {
      await dataApi.markAllAlertsAsRead()

      // Update the local state
      userAlerts.value = userAlerts.value.map((alert) => ({
        ...alert,
        is_read: true,
        read_at: new Date().toISOString(),
      }))

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to mark all alerts as read'
      message.error(error.value)
      return false
    }
  }

  // Admin-only actions
  const createMeasurement = async (data: Partial<EnvironmentalMeasurement>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await dataApi.createMeasurement(data)
      // Add to local state
      measurements.value.unshift(response.data)
      message.success('Measurement created successfully')
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create measurement'
      message.error(error.value)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updateMeasurement = async (id: number, data: Partial<EnvironmentalMeasurement>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await dataApi.updateMeasurement(id, data)
      // Update in local state
      const index = measurements.value.findIndex((m) => m.id === id)
      if (index !== -1) {
        measurements.value[index] = response.data
      }
      message.success('Measurement updated successfully')
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update measurement'
      message.error(error.value)
      return null
    } finally {
      isLoading.value = false
    }
  }

  const deleteMeasurement = async (id: number) => {
    isLoading.value = true
    error.value = null

    try {
      await dataApi.deleteMeasurement(id)
      // Remove from local state
      measurements.value = measurements.value.filter((m) => m.id !== id)
      message.success('Measurement deleted successfully')
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete measurement'
      message.error(error.value)
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    dashboardData,
    measurements,
    predictions,
    alerts,
    userAlerts,
    isLoading,
    error,

    // Computed
    latestMeasurements,
    upcomingPredictions,
    activeAlerts,
    unreadUserAlerts,

    // Actions
    fetchDashboardData,
    fetchMeasurements,
    fetchPredictions,
    fetchAlerts,
    fetchUserAlerts,
    markAlertAsRead,
    markAllAlertsAsRead,

    // Admin-only actions
    createMeasurement,
    updateMeasurement,
    deleteMeasurement,

    // Creating prediction and alert actions would be implemented similarly to above
  }
})
