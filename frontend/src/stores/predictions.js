import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const usePredictionsStore = defineStore('predictions', () => {
  const predictions = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function generatePredictions(location, hoursAhead = 24) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.post('/predictions/generate/', {
        location_name: location,
        hours_ahead: hoursAhead
      })
      predictions.value = response.data.predictions
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to generate predictions'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchPredictions(filters = {}) {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get('/predictions/', { params: filters })
      predictions.value = response.data.results || []
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch predictions'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    predictions,
    loading,
    error,
    generatePredictions,
    fetchPredictions
  }
})