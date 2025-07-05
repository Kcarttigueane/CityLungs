<template>
    <div class="metric-card bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium text-gray-600">{{ title }}</h3>
            <span :class="statusClass" class="text-xs font-semibold px-2 py-1 rounded">
                {{ statusText }}
            </span>
        </div>

        <div class="flex items-baseline">
            <span class="text-3xl font-bold text-gray-900">{{ value }}</span>
            <span class="ml-1 text-sm text-gray-600">{{ unit }}</span>
        </div>

        <div class="mt-4 flex items-center text-sm">
            <component :is="trendIcon" class="w-4 h-4 mr-1" :class="trendClass" />
            <span :class="trendClass">{{ trendText }}</span>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue'
import {
    ArrowUpIcon,
    ArrowDownIcon,
    MinusIcon
} from '@heroicons/vue/24/solid'

const props = defineProps({
    title: String,
    value: Number,
    unit: String,
    trend: String,
    status: String
})

const statusClass = computed(() => {
    const classes = {
        good: 'bg-green-100 text-green-800',
        moderate: 'bg-yellow-100 text-yellow-800',
        warning: 'bg-orange-100 text-orange-800',
        danger: 'bg-red-100 text-red-800'
    }
    return classes[props.status] || classes.moderate
})

const statusText = computed(() => {
    return props.status?.charAt(0).toUpperCase() + props.status?.slice(1) || 'Unknown'
})

const trendIcon = computed(() => {
    const icons = {
        up: ArrowUpIcon,
        down: ArrowDownIcon,
        stable: MinusIcon
    }
    return icons[props.trend] || MinusIcon
})

const trendClass = computed(() => {
    const classes = {
        up: 'text-red-600',
        down: 'text-green-600',
        stable: 'text-gray-600'
    }
    return classes[props.trend] || 'text-gray-600'
})

const trendText = computed(() => {
    const texts = {
        up: 'Increasing',
        down: 'Decreasing',
        stable: 'Stable'
    }
    return texts[props.trend] || 'No change'
})
</script>