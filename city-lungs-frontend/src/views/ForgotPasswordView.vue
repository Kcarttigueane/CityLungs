<template>
  <div class="auth-container">
    <!-- Left side with background image and branding -->
    <div class="auth-banner">
      <div class="auth-overlay">
        <div class="brand-content">
          <h1 class="brand-title">Smart City</h1>
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

    <!-- Right side with forgot password form -->
    <div class="auth-content">
      <div class="auth-card-container">
        <div v-if="!resetRequested">
          <div class="auth-form-header">
            <h2>Reset Password</h2>
            <p>Enter your email to receive password reset instructions</p>
          </div>

          <a-form
            :model="formState"
            name="reset-form"
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

            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="isLoading" size="large" block>
                Send Reset Instructions
              </a-button>
            </a-form-item>
          </a-form>
        </div>

        <div v-else class="reset-success">
          <a-result
            status="success"
            title="Reset Email Sent"
            sub-title="We've sent password reset instructions to your email address. Please check your inbox."
          >
            <template #extra>
              <a-button type="primary" @click="goToLogin"> Back to Login </a-button>
            </template>
          </a-result>
        </div>

        <div class="back-to-login">
          <router-link to="/login"> <left-outlined /> Back to Login </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { message } from 'ant-design-vue'
import {
  MailOutlined,
  LeftOutlined,
  EnvironmentOutlined,
  BarChartOutlined,
  NotificationOutlined,
} from '@ant-design/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// State
const resetRequested = ref(false)

// Form state
const formState = reactive({
  email: '',
})

// Computed properties
const isLoading = computed(() => authStore.isLoading)

// Methods
const handleSubmit = async () => {
  try {
    // Assuming your authStore has a requestPasswordReset method
    // const success = await authStore.requestPasswordReset(formState.email)
    // if (success) {
    //   resetRequested.value = true
    // }
    console.log('Password reset request sent')
  } catch (error) {
    console.error('Password reset request error:', error)
    message.error('Failed to send reset instructions. Please try again.')
  }
}

const goToLogin = () => {
  router.push('/login')
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

.reset-success {
  padding: 1rem 0;
}

.back-to-login {
  text-align: center;
  margin-top: 1.5rem;
}

.back-to-login a {
  color: rgba(0, 0, 0, 0.65);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.back-to-login a:hover {
  color: #1890ff;
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
