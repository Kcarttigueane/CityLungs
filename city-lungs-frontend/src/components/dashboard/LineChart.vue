<script setup lang="ts">
import { defineProps, defineExpose, watch, ref } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  type ChartData,
  type ChartOptions,
} from 'chart.js'
import { Line } from 'vue-chartjs'

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

// Define props
const props = defineProps<{
  chartData: ChartData<'line'>
  options?: ChartOptions<'line'>
}>()

// Reference to the Line chart component
const lineChart = ref<unknown>(null)

// Update chart method
const updateChart = () => {
  if (lineChart.value) {
    console.log('Updating chart')
    // lineChart.value.update()
  }
}

// Watch for changes in chartData
watch(
  () => props.chartData,
  () => {
    updateChart()
  },
  { deep: true },
)

// Expose methods
defineExpose({
  updateChart,
})
</script>

<template>
  <Line
    ref="lineChart"
    :data="chartData"
    :options="options || {}"
    style="width: 100%; height: 300px"
  />
</template>
