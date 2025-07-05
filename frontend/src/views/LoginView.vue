<template>
    <div class="min-h-screen flex items-center justify-center bg-gray-50">
        <div class="max-w-md w-full space-y-8">
            <div>
                <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
                    Sign in to Smart City Platform
                </h2>
            </div>
            <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
                <div class="rounded-md shadow-sm -space-y-px">
                    <div>
                        <label for="username" class="sr-only">Username</label>
                        <input id="username" v-model="form.username" name="username" type="text" required
                            class="form-input rounded-t-md" placeholder="Username" />
                    </div>
                    <div>
                        <label for="password" class="sr-only">Password</label>
                        <input id="password" v-model="form.password" name="password" type="password" required
                            class="form-input rounded-b-md" placeholder="Password" />
                    </div>
                </div>

                <div v-if="error" class="rounded-md bg-red-50 p-4">
                    <p class="text-sm text-red-800">{{ error }}</p>
                </div>

                <div>
                    <button type="submit" :disabled="loading" class="btn btn-primary w-full">
                        {{ loading ? 'Signing in...' : 'Sign in' }}
                    </button>
                </div>

                <div class="text-center">
                    <router-link to="/register" class="text-sm text-primary-600 hover:text-primary-500">
                        Don't have an account? Register
                    </router-link>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
    username: '',
    password: ''
})

const loading = ref(false)
const error = ref('')

async function handleLogin() {
    loading.value = true
    error.value = ''

    const result = await authStore.login(form)

    if (result.success) {
        router.push('/dashboard')
    } else {
        error.value = result.error
    }

    loading.value = false
}
</script>