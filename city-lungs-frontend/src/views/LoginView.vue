<template>
  <div class="auth-container">
    <!-- Left side with background image and branding -->
    <div class="auth-banner">
      <div class="auth-overlay">
        <div class="brand-content">
          <h1 class="brand-title">City Lungs</h1>
          <p class="brand-tagline">Environmental Monitoring Platform</p>
          <div class="brand-features">
            <div class="feature-item">
              <environment-outlined />
              <span>Real-time environmental data</span>
            </div>
            <div class="feature-item">
              <bar-chart-outlined />
              <span>Advanced analytics</span>
            </div>
            <div class="feature-item">
              <notification-outlined />
              <span>Instant alerts</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right side with login form -->
    <div class="auth-content">
      <div class="auth-card-container">
        <div class="auth-form-header">
          <h2>Welcome Back</h2>
          <p>Sign in to access your dashboard</p>
        </div>

        <a-form
          :model="formState"
          name="login-form"
          @finish="handleSubmit"
          layout="vertical"
          :hide-required-mark="true"
        >
          <a-form-item
            name="email"
            :rules="[
              { required: true, message: 'Please input your email' },
              { type: 'email', message: 'Please enter a valid email address' },
            ]"
          >
            <a-input
              v-model:value="formState.email"
              placeholder="Email"
              size="large"
              :prefix="h(MailOutlined)"
            />
          </a-form-item>

          <a-form-item
            name="password"
            :rules="[{ required: true, message: 'Please input your password' }]"
          >
            <a-input-password
              v-model:value="formState.password"
              placeholder="Password"
              size="large"
              :prefix="h(LockOutlined)"
            />
          </a-form-item>

          <div class="form-options">
            <a-checkbox v-model:checked="rememberMe">Remember me</a-checkbox>
            <router-link to="/forgot-password" class="forgot-link">Forgot password?</router-link>
          </div>

          <a-form-item>
            <a-button type="primary" html-type="submit" :loading="isLoading" size="large" block>
              Sign In
            </a-button>
          </a-form-item>
        </a-form>

        <div class="auth-divider">
          <span class="divider-text">OR</span>
        </div>

        <div class="social-login">
          <a-button size="large" class="social-btn google-btn" block>
            <template #icon><google-outlined /></template>
            Continue with Google
          </a-button>
        </div>

        <div class="register-link">
          Don't have an account? <router-link to="/register">Sign up</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { LoginCredentials } from '@/types'
import {
  MailOutlined,
  LockOutlined,
  GoogleOutlined,
  EnvironmentOutlined,
  BarChartOutlined,
  NotificationOutlined,
} from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Form state
const formState = reactive<LoginCredentials>({
  email: '',
  password: '',
})

const rememberMe = ref(false)

// For use with the h() function for icons

// Computed properties
const isLoading = computed(() => authStore.isLoading)

// Methods
const handleSubmit = async () => {
  const credentials = {
    ...formState,
    remember: rememberMe.value,
  }

  const success = await authStore.login(credentials)

  // If successful login and there's a redirect query parameter, redirect to that URL
  if (success && route.query.redirect) {
    const redirectPath = route.query.redirect as string
    router.push(redirectPath)
  } else if (success) {
    router.push('/dashboard')
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  position: absolute;
  top: 0;
  left: 0;
}

.auth-banner {
  flex: 1;
  background-image: url('/api/placeholder/800/1200');
  background-size: cover;
  background-position: center;
  position: relative;
  display: none;
}

.auth-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.9) 0%, rgba(0, 21, 41, 0.8) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 2rem;
  color: white;
}

.brand-content {
  max-width: 500px;
  margin: 0 auto;
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.brand-tagline {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.brand-features {
  margin-top: 3rem;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.feature-item span {
  margin-left: 1rem;
}

.auth-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background-color: #f5f5f5;
  overflow-y: auto;
}

.auth-card-container {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin: 2rem 0;
}

.auth-form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-form-header h2 {
  font-size: 1.8rem;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 0.5rem;
}

.auth-form-header p {
  color: rgba(0, 0, 0, 0.45);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.forgot-link {
  color: #1890ff;
  font-size: 0.9rem;
}

.auth-divider {
  position: relative;
  margin: 1.5rem 0;
  text-align: center;
}

.auth-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 1px;
  background-color: #f0f0f0;
}

.divider-text {
  position: relative;
  background-color: white;
  padding: 0 10px;
  color: rgba(0, 0, 0, 0.45);
  font-size: 0.9rem;
}

.social-login {
  margin-bottom: 1.5rem;
}

.social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e8e8e8;
}

.google-btn {
  background-color: white;
  color: rgba(0, 0, 0, 0.65);
}

.register-link {
  text-align: center;
  margin-top: 1.5rem;
  color: rgba(0, 0, 0, 0.45);
  font-size: 0.9rem;
}

.register-link a {
  color: #1890ff;
  font-weight: 500;
}

/* Responsive styles */
@media (min-width: 992px) {
  .auth-banner {
    display: block;
  }

  .auth-content {
    flex: 0 0 50%;
  }
}

@media (max-width: 576px) {
  .auth-card-container {
    padding: 1.5rem;
  }
}
</style>
