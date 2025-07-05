<template>
    <nav class="bg-white shadow">
        <div class="container mx-auto px-4">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center">
                    <router-link to="/" class="text-xl font-bold text-gray-900">
                        Smart City Platform
                    </router-link>

                    <div class="hidden md:flex ml-10 space-x-4">
                        <router-link v-for="item in navigation" :key="item.name" :to="item.to"
                            class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                            :class="{ 'bg-gray-100': $route.path === item.to }">
                            {{ item.name }}
                        </router-link>
                    </div>
                </div>

                <div class="flex items-center space-x-4">
                    <span class="text-sm text-gray-600">
                        {{ user?.username }}
                    </span>
                    <button @click="logout" class="btn btn-secondary text-sm">
                        Logout
                    </button>
                </div>
            </div>
        </div>
    </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.user)
const isAdmin = computed(() => authStore.isAdmin)

const navigation = computed(() => {
    const items = [
        { name: 'Dashboard', to: '/dashboard' },
        { name: 'Predictions', to: '/predictions' },
        { name: 'Alerts', to: '/alerts' }
    ]

    if (isAdmin.value) {
        items.push({ name: 'Admin', to: '/admin' })
    }

    return items
})

function logout() {
    authStore.logout()
    router.push('/login')
}
</script>