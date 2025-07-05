<template>
    <div ref="mapContainer" class="h-96 rounded-lg"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({
    locations: {
        type: Array,
        default: () => []
    }
})

const mapContainer = ref(null)
let map = null
let markers = []

const getMarkerColor = (aqi) => {
    if (aqi <= 50) return 'green'
    if (aqi <= 100) return 'yellow'
    if (aqi <= 150) return 'orange'
    return 'red'
}

const createCustomIcon = (color) => {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="background-color: ${color}; width: 30px; height: 30px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    })
}

const initMap = () => {
    if (!mapContainer.value) return

    map = L.map(mapContainer.value).setView([48.8566, 2.3522], 12)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map)

    updateMarkers()
}

const updateMarkers = () => {
    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker))
    markers = []

    // Add new markers
    props.locations.forEach(location => {
        const color = getMarkerColor(location.aqi)
        const icon = createCustomIcon(color)

        const marker = L.marker([location.lat, location.lng], { icon })
            .addTo(map)
            .bindPopup(`
          <div class="p-2">
            <h3 class="font-bold">${location.name}</h3>
            <p>PM2.5: ${location.pm25} μg/m³</p>
            <p>AQI: ${location.aqi}</p>
          </div>
        `)

        markers.push(marker)
    })
}

onMounted(() => {
    initMap()
})

watch(() => props.locations, updateMarkers, { deep: true })
</script>