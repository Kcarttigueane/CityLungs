<template>
    <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div class="container mx-auto px-4 py-16">
            <div class="text-center">
                <h1 class="text-5xl font-bold text-gray-900 mb-4">
                    Smart City Environmental Platform
                </h1>
                <p class="text-xl text-gray-600 mb-8">
                    Real-time air quality monitoring and prediction for healthier cities
                </p>

                <div v-if="!isAuthenticated" class="space-x-4">
                    <router-link to="/login" class="btn btn-primary inline-block">
                        Sign In
                    </router-link>
                    <router-link to="/register" class="btn btn-secondary inline-block">
                        Register
                    </router-link>
                </div>

                <div v-else>
                    <router-link to="/dashboard" class="btn btn-primary inline-block">
                        Go to Dashboard
                    </router-link>
                </div>
            </div>

            <div class="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div class="text-4xl mb-4">🌍</div>
                    <h3 class="text-xl font-semibold mb-2">Real-time Monitoring</h3>
                    <p class="text-gray-600">
                        Track air quality, weather, and environmental conditions in real-time
                    </p>
                </div>

                <div class="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div class="text-4xl mb-4">🤖</div>
                    <h3 class="text-xl font-semibold mb-2">AI Predictions</h3>
                    <p class="text-gray-600">
                        Advanced machine learning models predict PM2.5 levels 48 hours ahead
                    </p>
                </div>

                <div class="bg-white rounded-lg shadow-lg p-6 text-center">
                    <div class="text-4xl mb-4">🚨</div>
                    <h3 class="text-xl font-semibold mb-2">Smart Alerts</h3>
                    <p class="text-gray-600">
                        Receive timely alerts when air quality exceeds safe thresholds
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>
