<template>
    <div class="min-h-screen flex items-center justify-center bg-gray-50">
        <div class="max-w-md w-full space-y-8">
            <div>
                <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
                    Create your account
                </h2>
            </div>
            <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
                <div class="space-y-4">
                    <div>
                        <label for="username" class="block text-sm font-medium text-gray-700">
                            Username
                        </label>
                        <input id="username" v-model="form.username" name="username" type="text" required
                            class="form-input mt-1" />
                    </div>

                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-700">
                            Email
                        </label>
                        <input id="email" v-model="form.email" name="email" type="email" required
                            class="form-input mt-1" />
                    </div>

                    <div>
                        <label for="password" class="block text-sm font-medium text-gray-700">
                            Password
                        </label>
                        <input id="password" v-model="form.password" name="password" type="password" required
                            class="form-input mt-1" />
                    </div>

                    <div>
                        <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
                            Confirm Password
                        </label>
                        <input id="confirmPassword" v-model="form.confirmPassword" name="confirmPassword"
                            type="password" required class="form-input mt-1" />
                    </div>
                </div>

                <div v-if="error" class="rounded-md bg-red-50 p-4">
                    <p class="text-sm text-red-800">{{ error }}</p>
                </div>

                <div>
                    <button type="submit" :disabled="loading" class="btn btn-primary w-full">
                        {{ loading ? 'Creating account...' : 'Register' }}
                    </button>
                </div>

                <div class="text-center">
                    <router-link to="/login" class="text-sm text-primary-600 hover:text-primary-500">
                        Already have an account? Sign in
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
    email: '',
    password: '',
    confirmPassword: ''
})

const loading = ref(false)
const error = ref('')

async function handleRegister() {
    loading.value = true
    error.value = ''

    if (form.password !== form.confirmPassword) {
        error.value = 'Passwords do not match'
        loading.value = false
        return
    }

    const result = await authStore.register({
        username: form.username,
        email: form.email,
        password: form.password
    })

    if (result.success) {
        router.push('/login')
    } else {
        error.value = result.error
    }

    loading.value = false
}
</script>