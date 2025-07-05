<template>
    <div class="predictions-view container mx-auto px-4 py-8">
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900">PM2.5 Predictions</h1>
            <p class="mt-2 text-gray-600">Air quality forecasts for the next 48 hours</p>
        </div>

        <!-- Location Selector -->
        <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
                Select Location
            </label>
            <select v-model="selectedLocation" @change="loadPredictions" class="form-input w-full md:w-1/3">
                <option value="">Choose a location</option>
                <option v-for="loc in locations" :key="loc.id" :value="loc.name">
                    {{ loc.name }}
                </option>
            </select>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="flex justify-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>

        <!-- Predictions Chart -->
        <div v-else-if="predictions.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">24-Hour Forecast</h2>
                <p class="text-sm text-gray-600 mb-4">Predictions loaded: {{ predictions.length }}</p>
                <div v-if="chartData24h.labels && chartData24h.labels.length > 0">
                    <Line :data="chartData24h" :options="chartOptions" />
                </div>
                <div v-else class="text-gray-500">
                    No chart data available. Debug info:
                    <pre class="text-xs">{{ JSON.stringify(chartData24h, null, 2) }}</pre>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">48-Hour Forecast</h2>
                <div v-if="chartData48h.labels && chartData48h.labels.length > 0">
                    <Line :data="chartData48h" :options="chartOptions" />
                </div>
                <div v-else class="text-gray-500">
                    No chart data available
                </div>
            </div>

            <!-- Debug Section -->
            <div class="bg-gray-50 rounded-lg shadow p-6 lg:col-span-2">
                <h2 class="text-xl font-semibold mb-4">Debug Information</h2>
                <div class="text-sm">
                    <p><strong>Total predictions:</strong> {{ predictions.length }}</p>
                    <p><strong>Random Forest:</strong> {{ predictions.filter(p => p.model === 'random_forest').length }}</p>
                    <p><strong>XGBoost:</strong> {{ predictions.filter(p => p.model === 'xgboost').length }}</p>
                    <p><strong>Ensemble:</strong> {{ predictions.filter(p => p.model === 'ensemble').length }}</p>
                    <details class="mt-4">
                        <summary class="cursor-pointer">Sample predictions (click to expand)</summary>
                        <pre class="text-xs mt-2 overflow-auto">{{ JSON.stringify(predictions.slice(0, 6), null, 2) }}</pre>
                    </details>
                </div>
            </div>

            <!-- Model Comparison -->
            <div class="bg-white rounded-lg shadow p-6 lg:col-span-2">
                <h2 class="text-xl font-semibold mb-4">Model Comparison</h2>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Model
                                </th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    24h Avg PM2.5
                                </th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    48h Avg PM2.5
                                </th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Confidence
                                </th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            <tr v-for="model in modelComparison" :key="model.name">
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {{ model.name }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {{ model.avg24h.toFixed(1) }} μg/m³
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {{ model.avg48h.toFixed(1) }} μg/m³
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span :class="getConfidenceBadgeClass(model.confidence)">
                                        {{ (model.confidence * 100).toFixed(0) }}%
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-12">
            <p class="text-gray-500">Select a location to view predictions</p>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import api from '@/services/api'
import { format } from 'date-fns'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const selectedLocation = ref('')
const predictions = ref([])
const loading = ref(false)

const locations = ref([
    { id: 1, name: 'Paris City Center' },
    { id: 2, name: 'Paris Nord' },
    { id: 3, name: 'Paris Est' }
])

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom'
        },
        tooltip: {
            callbacks: {
                label: (context) => {
                    return `${context.dataset.label}: ${context.parsed.y.toFixed(1)} μg/m³`
                }
            }
        }
    },
    scales: {
        x: {
            type: 'category'
        },
        y: {
            type: 'linear',
            title: {
                display: true,
                text: 'PM2.5 (μg/m³)'
            },
            beginAtZero: false
        }
    }
}

const chartData24h = computed(() => {
    if (!predictions.value || predictions.value.length === 0) {
        return {
            labels: [],
            datasets: []
        }
    }
    
    console.log('All predictions:', predictions.value.length)
    console.log('Sample prediction:', predictions.value[0])
    
    // Group by model type first
    const modelGroups = {
        random_forest: predictions.value.filter(p => p.model === 'random_forest'),
        xgboost: predictions.value.filter(p => p.model === 'xgboost'), 
        ensemble: predictions.value.filter(p => p.model === 'ensemble')
    }
    
    console.log('Model groups:', Object.keys(modelGroups).map(k => ({model: k, count: modelGroups[k].length})))
    
    // Take first 24 hours from each model
    const data24h = {
        random_forest: modelGroups.random_forest.slice(0, 24),
        xgboost: modelGroups.xgboost.slice(0, 24),
        ensemble: modelGroups.ensemble.slice(0, 24)
    }
    
    // Create labels from one of the models
    const labels = data24h.random_forest.map(p =>
        format(new Date(p.timestamp), 'HH:mm')
    )

    return {
        labels,
        datasets: [
            {
                label: 'Random Forest',
                data: data24h.random_forest.map(p => p.pm25),
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4
            },
            {
                label: 'XGBoost',
                data: data24h.xgboost.map(p => p.pm25),
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4
            },
            {
                label: 'Ensemble',
                data: data24h.ensemble.map(p => p.pm25),
                borderColor: 'rgb(245, 158, 11)',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.4,
                borderWidth: 3
            }
        ]
    }
})

const chartData48h = computed(() => {
    if (!predictions.value || predictions.value.length === 0) {
        return {
            labels: [],
            datasets: []
        }
    }
    
    // Get ensemble predictions for 48-hour view
    const ensemblePredictions = predictions.value.filter(p => p.model === 'ensemble')
    
    return {
        labels: ensemblePredictions.map(p =>
            format(new Date(p.timestamp), 'MM/dd HH:mm')
        ),
        datasets: [
            {
                label: 'Ensemble Prediction',
                data: ensemblePredictions.map(p => p.pm25),
                borderColor: 'rgb(245, 158, 11)',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.4
            }
        ]
    }
})

const modelComparison = computed(() => {
    if (!predictions.value || predictions.value.length === 0) {
        return []
    }
    
    const models = ['random_forest', 'xgboost', 'ensemble']

    return models.map(model => {
        const modelPreds = predictions.value.filter(p => p.model === model)
        const preds24h = modelPreds.slice(0, 24)
        const preds48h = modelPreds

        return {
            name: model.replace('_', ' ').split(' ').map(w =>
                w.charAt(0).toUpperCase() + w.slice(1)
            ).join(' '),
            avg24h: preds24h.length > 0 ? preds24h.reduce((sum, p) => sum + p.pm25, 0) / preds24h.length : 0,
            avg48h: preds48h.length > 0 ? preds48h.reduce((sum, p) => sum + p.pm25, 0) / preds48h.length : 0,
            confidence: preds24h[0]?.confidence || 0
        }
    }).filter(m => m.avg24h > 0) // Only show models with data
})

async function loadPredictions() {
    if (!selectedLocation.value) return

    loading.value = true
    try {
        const response = await api.post('/predictions/generate/', {
            location_name: selectedLocation.value,
            hours_ahead: 48
        })
        
        // Transform backend format to frontend format
        predictions.value = response.data.map(pred => ({
            pm25: parseFloat(pred.predicted_pm25),
            confidence: parseFloat(pred.confidence_score),
            model: pred.model_name,
            timestamp: pred.target_timestamp
        }))
        
        console.log('Loaded predictions:', predictions.value.length)
        console.log('Sample transformed prediction:', predictions.value[0])
    } catch (error) {
        console.error('Failed to load predictions:', error)
        console.error('Error details:', error.response?.data || error.message)
    } finally {
        loading.value = false
    }
}

function getConfidenceBadgeClass(confidence) {
    if (confidence >= 0.9) return 'px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800'
    if (confidence >= 0.8) return 'px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800'
    return 'px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800'
}

onMounted(() => {
    if (locations.value.length > 0) {
        selectedLocation.value = locations.value[0].name
        loadPredictions()
    }
})
</script>