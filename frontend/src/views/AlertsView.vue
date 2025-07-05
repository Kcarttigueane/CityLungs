<template>
    <div class="alerts-view container mx-auto px-4 py-8">
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900">Environmental Alerts</h1>
            <p class="mt-2 text-gray-600">Active alerts and notifications</p>
        </div>

        <!-- Alert Summary -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div v-for="severity in ['critical', 'high', 'medium', 'low']" :key="severity"
                class="bg-white rounded-lg shadow p-4">
                <div class="flex items-center">
                    <div :class="getSeverityIconClass(severity)" class="rounded-full p-2 mr-3">
                        <ExclamationTriangleIcon class="h-6 w-6" />
                    </div>
                    <div>
                        <p class="text-sm text-gray-600">{{ severity.charAt(0).toUpperCase() + severity.slice(1) }}</p>
                        <p class="text-2xl font-bold">{{ getAlertCount(severity) }}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Active Alerts List -->
        <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-xl font-semibold">Active Alerts</h2>
            </div>

            <div v-if="loading" class="p-6 text-center">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            </div>

            <div v-else-if="alerts.length === 0" class="p-6 text-center text-gray-500">
                No active alerts at this time
            </div>

            <div v-else class="divide-y divide-gray-200">
                <div v-for="alert in alerts" :key="alert.id" class="p-6 hover:bg-gray-50 transition-colors">
                    <div class="flex items-start justify-between">
                        <div class="flex items-start">
                            <div :class="getSeverityIconClass(alert.severity)" class="rounded-full p-2 mr-4">
                                <ExclamationTriangleIcon class="h-5 w-5" />
                            </div>
                            <div>
                                <h3 class="text-lg font-medium text-gray-900">
                                    {{ alert.alert_type }} Alert
                                </h3>
                                <p class="mt-1 text-sm text-gray-600">
                                    {{ alert.message }}
                                </p>
                                <div class="mt-2 flex items-center text-sm text-gray-500">
                                    <MapPinIcon class="h-4 w-4 mr-1" />
                                    {{ alert.location_name }}
                                    <span class="mx-2">•</span>
                                    <ClockIcon class="h-4 w-4 mr-1" />
                                    {{ formatTime(alert.created_at) }}
                                </div>
                                <div v-if="alert.threshold_value" class="mt-2 text-sm">
                                    <span class="text-gray-600">Threshold:</span>
                                    <span class="font-medium">{{ alert.threshold_value }}</span>
                                    <span class="mx-2">→</span>
                                    <span class="text-gray-600">Actual:</span>
                                    <span class="font-medium text-red-600">{{ alert.actual_value }}</span>
                                </div>
                            </div>
                        </div>

                        <button v-if="isAdmin" @click="resolveAlert(alert.id)" class="btn btn-secondary text-sm">
                            Resolve
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alert History -->
        <div class="mt-8 bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-xl font-semibold">Alert History (Last 7 Days)</h2>
            </div>
            <div class="p-6">
                <Bar :data="historyChartData" :options="historyChartOptions" />
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import { format, parseISO } from 'date-fns'
import {
    ExclamationTriangleIcon,
    MapPinIcon,
    ClockIcon
} from '@heroicons/vue/24/outline'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin)

const alerts = ref([])
const loading = ref(false)

const historyChartData = computed(() => ({
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
        {
            label: 'Critical',
            data: [2, 1, 0, 3, 2, 1, 0],
            backgroundColor: 'rgb(239, 68, 68)'
        },
        {
            label: 'High',
            data: [3, 2, 4, 2, 3, 2, 1],
            backgroundColor: 'rgb(251, 146, 60)'
        },
        {
            label: 'Medium',
            data: [5, 4, 6, 5, 4, 3, 2],
            backgroundColor: 'rgb(251, 191, 36)'
        },
        {
            label: 'Low',
            data: [8, 6, 7, 9, 7, 5, 4],
            backgroundColor: 'rgb(34, 197, 94)'
        }
    ]
}))

const historyChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom'
        }
    },
    scales: {
        x: {
            stacked: true
        },
        y: {
            stacked: true,
            title: {
                display: true,
                text: 'Number of Alerts'
            }
        }
    }
}

function getSeverityIconClass(severity) {
    const classes = {
        critical: 'bg-red-100 text-red-600',
        high: 'bg-orange-100 text-orange-600',
        medium: 'bg-yellow-100 text-yellow-600',
        low: 'bg-green-100 text-green-600'
    }
    return classes[severity] || classes.medium
}

function getAlertCount(severity) {
    return alerts.value.filter(a => a.severity === severity).length
}

function formatTime(timestamp) {
    return format(parseISO(timestamp), 'MMM dd, HH:mm')
}

async function loadAlerts() {
    loading.value = true
    try {
        const response = await api.get('/alerts/', {
            params: { is_active: true }
        })
        alerts.value = response.data.results || []
    } catch (error) {
        console.error('Failed to load alerts:', error)
    } finally {
        loading.value = false
    }
}

async function resolveAlert(alertId) {
    try {
        await api.post(`/alerts/${alertId}/resolve/`)
        await loadAlerts()
    } catch (error) {
        console.error('Failed to resolve alert:', error)
    }
}

onMounted(() => {
    loadAlerts()

    // Refresh alerts every 30 seconds
    const interval = setInterval(loadAlerts, 30000)

    // Clean up on unmount
    return () => clearInterval(interval)
})
</script>