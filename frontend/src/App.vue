<template>
    <div id="app">
        <nav-bar v-if="isAuthenticated" />
        <router-view />
        <notification-toast ref="notificationToast" />
    </div>
</template>

<script setup>
import { computed, onMounted, provide, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import NavBar from '@/components/NavBar.vue'
import NotificationToast from '@/components/NotificationToast.vue'

const authStore = useAuthStore()
const notificationToast = ref(null)

const isAuthenticated = computed(() => authStore.isAuthenticated)

// Provide notification method globally
provide('notify', (type, title, message) => {
    notificationToast.value?.showNotification(type, title, message)
})

onMounted(() => {
    // Check if user is logged in on app mount
    if (authStore.token && !authStore.user) {
        // Optionally fetch user profile here
    }
})
</script>

<style>
#app {
    min-height: 100vh;
    background-color: #f3f4f6;
}
</style>