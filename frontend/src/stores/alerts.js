import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useAlertsStore = defineStore('alerts', () => {
  const alerts = ref([])
  const alertConfigs = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchAlerts(filters = {}) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/alerts/', { params: filters })
      alerts.value = response.data.results || []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch alerts'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function resolveAlert(alertId) {
    try {
      await api.post(`/alerts/${alertId}/resolve/`)
      // Update local state
      const alert = alerts.value.find(a => a.id === alertId)
      if (alert) {
        alert.is_active = false
        alert.resolved_at = new Date().toISOString()
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to resolve alert'
      throw err
    }
  }

  async function fetchAlertConfigs() {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/alert-configs/')
      alertConfigs.value = response.data.results || []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch alert configs'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createAlertConfig(config) {
    try {
      const response = await api.post('/alert-configs/', config)
      alertConfigs.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create alert config'
      throw err
    }
  }

  async function updateAlertConfig(id, updates) {
    try {
      const response = await api.patch(`/alert-configs/${id}/`, updates)
      const index = alertConfigs.value.findIndex(c => c.id === id)
      if (index !== -1) {
        alertConfigs.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update alert config'
      throw err
    }
  }

  async function deleteAlertConfig(id) {
    try {
      await api.delete(`/alert-configs/${id}/`)
      alertConfigs.value = alertConfigs.value.filter(c => c.id !== id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete alert config'
      throw err
    }
  }

  return {
    alerts,
    alertConfigs,
    loading,
    error,
    fetchAlerts,
    resolveAlert,
    fetchAlertConfigs,
    createAlertConfig,
    updateAlertConfig,
    deleteAlertConfig
  }
})