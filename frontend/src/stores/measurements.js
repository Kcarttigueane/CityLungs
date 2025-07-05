import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useMeasurementsStore = defineStore('measurements', () => {
  const measurements = ref([])
  const latestMeasurements = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchLatestMeasurements() {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/measurements/latest/')
      latestMeasurements.value = response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch measurements'
    } finally {
      loading.value = false
    }
  }

  async function fetchHistoricalData(location, days = 7) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/measurements/history/', {
        params: { location, days }
      })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch historical data'
      return []
    } finally {
      loading.value = false
    }
  }

  return {
    measurements,
    latestMeasurements,
    loading,
    error,
    fetchLatestMeasurements,
    fetchHistoricalData
  }
})