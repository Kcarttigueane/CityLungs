<template>
    <div class="dashboard">
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900">Environmental Dashboard</h1>
            <p class="mt-2 text-gray-600">Real-time monitoring of air quality and environmental conditions</p>
        </div>

        <!-- Metrics Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <MetricCard v-for="metric in metrics" :key="metric.id" :title="metric.title" :value="metric.value"
                :unit="metric.unit" :trend="metric.trend" :status="metric.status" />
        </div>

        <!-- Charts Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">PM2.5 Levels - Last 7 Days</h2>
                <div class="h-64">
                    <LineChart :data="pm25ChartData" :options="chartOptions" />
                </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold mb-4">Air Quality Index</h2>
                <div class="h-64">
                    <DoughnutChart :data="aqiChartData" :options="doughnutOptions" />
                </div>
            </div>
        </div>

        <!-- Map Section -->
        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold mb-4">Monitoring Locations</h2>
            <EnvironmentMap :locations="locations" />
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line as LineChart, Doughnut as DoughnutChart } from 'vue-chartjs'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    ArcElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js'
import MetricCard from '@/components/MetricCard.vue'
import EnvironmentMap from '@/components/EnvironmentMap.vue'
import { useMeasurementsStore } from '@/stores/measurements'

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    ArcElement,
    Title,
    Tooltip,
    Legend
)

const measurementsStore = useMeasurementsStore()

const metrics = ref([
    { id: 1, title: 'PM2.5', value: 35.2, unit: 'μg/m³', trend: 'up', status: 'warning' },
    { id: 2, title: 'Temperature', value: 22.5, unit: '°C', trend: 'stable', status: 'good' },
    { id: 3, title: 'Humidity', value: 65, unit: '%', trend: 'down', status: 'good' },
    { id: 4, title: 'AQI', value: 78, unit: '', trend: 'up', status: 'moderate' }
])

const locations = ref([
    { id: 1, name: 'City Center', lat: 48.8566, lng: 2.3522, pm25: 35.2, aqi: 78 },
    { id: 2, name: 'Industrial Zone', lat: 48.8606, lng: 2.3376, pm25: 45.8, aqi: 95 },
    { id: 3, name: 'Residential Area', lat: 48.8484, lng: 2.3534, pm25: 28.5, aqi: 65 }
])

const pm25ChartData = computed(() => ({
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
        {
            label: 'PM2.5 Levels',
            data: [32, 35, 38, 34, 36, 40, 35],
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4
        }
    ]
}))

const aqiChartData = computed(() => ({
    labels: ['Good', 'Moderate', 'Unhealthy', 'Very Unhealthy'],
    datasets: [
        {
            data: [25, 45, 20, 10],
            backgroundColor: [
                'rgb(34, 197, 94)',
                'rgb(251, 191, 36)',
                'rgb(251, 146, 60)',
                'rgb(239, 68, 68)'
            ]
        }
    ]
}))

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        }
    }
}

const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom'
        }
    }
}

onMounted(async () => {
    await measurementsStore.fetchLatestMeasurements()
    // Update metrics with real data
    updateMetrics()
})

function updateMetrics() {
    const latest = measurementsStore.latestMeasurements[0]
    if (latest) {
        metrics.value[0].value = parseFloat(latest.pm25) || 0
        metrics.value[1].value = parseFloat(latest.temperature) || 0
        metrics.value[2].value = parseFloat(latest.humidity) || 0
        metrics.value[3].value = parseFloat(latest.aqi) || 0
    }
}
</script>

<style scoped>
.dashboard {
    @apply container mx-auto px-4 py-8;
}
</style>