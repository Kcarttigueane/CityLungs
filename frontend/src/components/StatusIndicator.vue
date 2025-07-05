<template>
    <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-gray-700">{{ label }}</span>
        <div class="flex items-center">
            <div :class="statusClass" class="h-2 w-2 rounded-full mr-2" />
            <span class="text-sm text-gray-500">{{ statusText }}</span>
            <span v-if="lastUpdate" class="text-xs text-gray-400 ml-2">
                ({{ lastUpdate }})
            </span>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    label: String,
    status: String,
    lastUpdate: String
})

const statusClass = computed(() => {
    const classes = {
        online: 'bg-green-500',
        offline: 'bg-red-500',
        warning: 'bg-yellow-500'
    }
    return classes[props.status] || 'bg-gray-500'
})

const statusText = computed(() => {
    return props.status?.charAt(0).toUpperCase() + props.status?.slice(1) || 'Unknown'
})
</script>