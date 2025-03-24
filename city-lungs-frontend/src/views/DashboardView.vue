<template>
  <div class="dashboard-container">
    <a-page-header title="Dashboard" sub-title="Environmental Monitoring Overview">
      <template #extra>
        <a-input-search
          v-model:value="locationFilter"
          placeholder="Filter by location"
          style="width: 240px"
          @search="handleSearch"
        />
      </template>
    </a-page-header>

    <a-spin :spinning="isLoading">
      <a-row :gutter="[16, 16]">
        <!-- Stats Cards -->
        <a-col :span="6">
          <a-card class="stats-card">
            <template #title>
              <div class="stats-title">
                <safety-outlined />
                <span>Air Quality</span>
              </div>
            </template>
            <div v-if="latestPollutionMeasurement">
              <div class="stats-value">{{ getAQIValue() }}</div>
              <div class="stats-label" :style="{ color: getAQIColor() }">
                {{ getAQILabel() }}
              </div>
            </div>
            <a-empty v-else description="No data available" />
          </a-card>
        </a-col>

        <a-col :span="6">
          <a-card class="stats-card">
            <template #title>
              <div class="stats-title">
                <cloud-outlined />
                <span>Temperature</span>
              </div>
            </template>
            <div v-if="latestWeatherMeasurement?.temperature !== undefined">
              <div class="stats-value">{{ latestWeatherMeasurement.temperature }}°C</div>
              <div class="stats-label">
                {{ getTemperatureLabel(latestWeatherMeasurement.temperature) }}
              </div>
            </div>
            <a-empty v-else description="No data available" />
          </a-card>
        </a-col>

        <a-col :span="6">
          <a-card class="stats-card">
            <template #title>
              <div class="stats-title">
                <car-outlined />
                <span>Traffic</span>
              </div>
            </template>
            <div v-if="latestTrafficMeasurement?.traffic_volume !== undefined">
              <div class="stats-value">{{ latestTrafficMeasurement.traffic_volume }}</div>
              <div class="stats-label">
                {{ getTrafficLabel(latestTrafficMeasurement.traffic_volume) }}
              </div>
            </div>
            <a-empty v-else description="No data available" />
          </a-card>
        </a-col>

        <a-col :span="6">
          <a-card class="stats-card">
            <template #title>
              <div class="stats-title">
                <warning-outlined />
                <span>Active Alerts</span>
              </div>
            </template>
            <div>
              <div class="stats-value">{{ activeAlerts.length }}</div>
              <div class="stats-label">
                {{
                  activeAlerts.length === 0
                    ? 'No alerts'
                    : activeAlerts.length === 1
                      ? '1 alert'
                      : `${activeAlerts.length} alerts`
                }}
              </div>
            </div>
          </a-card>
        </a-col>
      </a-row>

      <!-- Charts Row -->
      <!-- <a-row :gutter="[16, 16]" style="margin-top: 16px">
        <a-col :span="12">
          <a-card title="Pollution Trends">
            <line-chart
              v-if="pollutionChartData.labels.length > 0"
              :chart-data="pollutionChartData"
              :options="pollutionChartOptions"
            />
            <a-empty v-else description="No data available" />
          </a-card>
        </a-col>

        <a-col :span="12">
          <a-card title="Temperature Trends">
            <line-chart
              v-if="temperatureChartData.labels.length > 0"
              :chart-data="temperatureChartData"
              :options="temperatureChartOptions"
            />
            <a-empty v-else description="No data available" />
          </a-card>
        </a-col>
      </a-row> -->

      <!-- Alerts and Predictions -->
      <a-row :gutter="[16, 16]" style="margin-top: 16px">
        <a-col :span="12">
          <a-card title="Active Alerts" class="dashboard-card">
            <template v-if="activeAlerts.length > 0">
              <a-list :data-source="activeAlerts" :pagination="{ pageSize: 3 }">
                <template #renderItem="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        <div>
                          <a-tag :color="getAlertSeverityColor(item.severity)">
                            {{ item.severity.toUpperCase() }}
                          </a-tag>
                          {{ item.title }}
                        </div>
                      </template>
                      <template #description>{{ item.description }}</template>
                      <!-- <template #avatar>
                        <a-avatar
                          :style="{ backgroundColor: getAlertTypeColor(item.alert_type) }"
                          :icon="getAlertTypeIcon(item.alert_type)"
                        />
                      </template> -->
                    </a-list-item-meta>
                    <template #extra>
                      <span>{{ formatDate(item.timestamp) }}</span>
                    </template>
                  </a-list-item>
                </template>
              </a-list>
            </template>
            <a-empty v-else description="No active alerts" />
          </a-card>
        </a-col>

        <a-col :span="12">
          <a-card title="Upcoming Predictions" class="dashboard-card">
            <template v-if="upcomingPredictions.length > 0">
              <a-list :data-source="upcomingPredictions" :pagination="{ pageSize: 3 }">
                <template #renderItem="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        <div>Prediction for {{ formatDate(item.target_time) }}</div>
                      </template>
                      <template #description>
                        <div>
                          <div>Location: {{ item.location }}</div>
                          <div>
                            PM2.5: {{ item.predicted_pm25 ?? 'N/A' }} µg/m³
                            {{
                              item.predicted_pm25
                                ? `(${getAQILabelFromPM25(item.predicted_pm25)})`
                                : ''
                            }}
                          </div>
                          <div>Traffic volume: {{ item.predicted_traffic ?? 'N/A' }}</div>
                        </div>
                      </template>
                      <template #avatar>
                        <a-avatar
                          :style="{ backgroundColor: '#1890ff' }"
                          icon="bar-chart-outlined"
                        />
                      </template>
                    </a-list-item-meta>
                    <template #extra>
                      <a-tag color="blue"> Model: {{ item.model_name }} </a-tag>
                    </template>
                  </a-list-item>
                </template>
              </a-list>
            </template>
            <a-empty v-else description="No upcoming predictions" />
          </a-card>
        </a-col>
      </a-row>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { SafetyOutlined, CloudOutlined, CarOutlined, WarningOutlined } from '@ant-design/icons-vue'
import { useDataStore } from '@/stores/data'
import type { Alert } from '@/types'

import type { ChartData } from 'chart.js'

const dataStore = useDataStore()
const locationFilter = ref('')
const isLoading = computed(() => dataStore.isLoading)

// Computed properties for the latest measurements
const latestMeasurements = computed(() => dataStore.latestMeasurements)
const upcomingPredictions = computed(() => dataStore.upcomingPredictions.slice(0, 10))
const activeAlerts = computed(() => dataStore.activeAlerts)

const latestPollutionMeasurement = computed(() => {
  return latestMeasurements.value.find((m) => m.pm25 !== undefined || m.pm10 !== undefined)
})

const latestWeatherMeasurement = computed(() => {
  return latestMeasurements.value.find((m) => m.temperature !== undefined)
})

const latestTrafficMeasurement = computed(() => {
  return latestMeasurements.value.find((m) => m.traffic_volume !== undefined)
})

// Chart data
const pollutionChartData = reactive<ChartData<'line'>>({
  labels: [],
  datasets: [
    {
      label: 'PM2.5',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      borderColor: 'rgba(75, 192, 192, 1)',
      data: [],
    },
    {
      label: 'PM10',
      backgroundColor: 'rgba(153, 102, 255, 0.2)',
      borderColor: 'rgba(153, 102, 255, 1)',
      data: [],
    },
  ],
})

// const pollutionChartOptions = reactive<ChartOptions<'line'>>({
//   responsive: true,
//   scales: {
//     y: {
//       beginAtZero: true,
//       title: {
//         display: true,
//         text: 'µg/m³',
//       },
//     },
//     x: {
//       title: {
//         display: true,
//         text: 'Time',
//       },
//     },
//   },
// })

const temperatureChartData = reactive<ChartData<'line'>>({
  labels: [],
  datasets: [
    {
      label: 'Temperature',
      backgroundColor: 'rgba(255, 99, 132, 0.2)',
      borderColor: 'rgba(255, 99, 132, 1)',
      data: [],
    },
  ],
})

// const temperatureChartOptions = reactive<ChartOptions<'line'>>({
//   responsive: true,
//   scales: {
//     y: {
//       beginAtZero: false,
//       title: {
//         display: true,
//         text: '°C',
//       },
//     },
//     x: {
//       title: {
//         display: true,
//         text: 'Time',
//       },
//     },
//   },
// })

// Methods
const handleSearch = async () => {
  await fetchDashboardData()
}

const fetchDashboardData = async () => {
  await dataStore.fetchDashboardData(locationFilter.value || undefined)
  updateChartData()
}

const updateChartData = () => {
  // Get pollution measurements with PM2.5 or PM10 data
  const pollutionMeasurements = dataStore.measurements
    .filter((m) => m.pm25 !== undefined || m.pm10 !== undefined)
    .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    .slice(-10) // Only take the last 10 entries

  // Update pollution chart data
  pollutionChartData.labels = pollutionMeasurements.map((m) =>
    new Date(m.timestamp).toLocaleTimeString(),
  )

  pollutionChartData.datasets[0].data = pollutionMeasurements.map((m) => m.pm25 || 0)
  pollutionChartData.datasets[1].data = pollutionMeasurements.map((m) => m.pm10 || 0)

  // Get temperature measurements
  const temperatureMeasurements = dataStore.measurements
    .filter((m) => m.temperature !== undefined)
    .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    .slice(-10) // Only take the last 10 entries

  // Update temperature chart data
  temperatureChartData.labels = temperatureMeasurements.map((m) =>
    new Date(m.timestamp).toLocaleTimeString(),
  )

  temperatureChartData.datasets[0].data = temperatureMeasurements.map((m) => m.temperature || 0)
}

// Helper methods for display
const getAQIValue = () => {
  if (!latestPollutionMeasurement.value) return 'N/A'

  const pm25 = latestPollutionMeasurement.value.pm25
  if (pm25 === undefined) return 'N/A'

  return pm25.toFixed(1)
}

const getAQILabel = () => {
  if (!latestPollutionMeasurement.value || latestPollutionMeasurement.value.pm25 === undefined)
    return 'No data'

  return getAQILabelFromPM25(latestPollutionMeasurement.value.pm25)
}

const getAQILabelFromPM25 = (pm25: number) => {
  if (pm25 <= 12) return 'Good'
  if (pm25 <= 35.4) return 'Moderate'
  if (pm25 <= 55.4) return 'Unhealthy for Sensitive Groups'
  if (pm25 <= 150.4) return 'Unhealthy'
  if (pm25 <= 250.4) return 'Very Unhealthy'
  return 'Hazardous'
}

const getAQIColor = () => {
  if (!latestPollutionMeasurement.value || latestPollutionMeasurement.value.pm25 === undefined)
    return '#d9d9d9'

  const pm25 = latestPollutionMeasurement.value.pm25

  if (pm25 <= 12) return '#52c41a' // Good - Green
  if (pm25 <= 35.4) return '#faad14' // Moderate - Yellow
  if (pm25 <= 55.4) return '#fa8c16' // Unhealthy for Sensitive Groups - Orange
  if (pm25 <= 150.4) return '#f5222d' // Unhealthy - Red
  if (pm25 <= 250.4) return '#722ed1' // Very Unhealthy - Purple
  return '#a8071a' // Hazardous - Dark Red
}

const getTemperatureLabel = (temp: number) => {
  if (temp < 0) return 'Very Cold'
  if (temp < 10) return 'Cold'
  if (temp < 20) return 'Cool'
  if (temp < 30) return 'Warm'
  if (temp < 35) return 'Hot'
  return 'Very Hot'
}

const getTrafficLabel = (volume: number) => {
  if (volume < 100) return 'Light'
  if (volume < 500) return 'Moderate'
  if (volume < 1000) return 'Heavy'
  return 'Very Heavy'
}

const getAlertSeverityColor = (severity: Alert['severity']) => {
  switch (severity) {
    case 'low':
      return 'green'
    case 'medium':
      return 'orange'
    case 'high':
      return 'volcano'
    case 'critical':
      return 'red'
    default:
      return 'blue'
  }
}

// const getAlertTypeColor = (type: Alert['alert_type']) => {
//   switch (type) {
//     case 'pollution':
//       return '#ff7a45'
//     case 'weather':
//       return '#1890ff'
//     case 'traffic':
//       return '#52c41a'
//     default:
//       return '#722ed1'
//   }
// }

// const getAlertTypeIcon = (type: Alert['alert_type']) => {
//   switch (type) {
//     case 'pollution':
//       return <AlertOutlined />
//     case 'weather':
//       return <ThunderboltOutlined />
//     case 'traffic':
//       return <CarOutlined />
//     default:
//       return <WarningOutlined />
//   }
// }

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

// Initialize dashboard
onMounted(async () => {
  await fetchDashboardData()
})
</script>

<style scoped>
.dashboard-container {
  padding: 0 16px;
}

.stats-card {
  height: 100%;
}

.stats-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 4px;
}

.stats-label {
  color: rgba(0, 0, 0, 0.45);
}

.dashboard-card {
  height: 400px;
  overflow: auto;
}
</style>
