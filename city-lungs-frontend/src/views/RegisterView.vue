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

    <!-- Right side with registration form -->
    <div class="auth-content">
      <div class="auth-card-container">
        <div class="auth-form-header">
          <h2>Create Account</h2>
          <p>Join the Smart City monitoring platform</p>
        </div>

        <a-form
          :model="formState"
          name="register-form"
          @finish="handleSubmit"
          layout="vertical"
          :hide-required-mark="true"
        >
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item
                name="first_name"
                :rules="[{ required: true, message: 'Please input your first name' }]"
              >
                <a-input
                  v-model:value="formState.first_name"
                  placeholder="First Name"
                  size="large"
                  :prefix="h(UserOutlined)"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item
                name="last_name"
                :rules="[{ required: true, message: 'Please input your last name' }]"
              >
                <a-input v-model:value="formState.last_name" placeholder="Last Name" size="large" />
              </a-form-item>
            </a-col>
          </a-row>

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
            :rules="[
              { required: true, message: 'Please input your password' },
              { min: 8, message: 'Password must be at least 8 characters' },
            ]"
          >
            <a-input-password
              v-model:value="formState.password"
              placeholder="Password"
              size="large"
              :prefix="h(LockOutlined)"
            />
          </a-form-item>

          <a-form-item
            name="password2"
            :rules="[
              { required: true, message: 'Please confirm your password' },
              { validator: validatePassword },
            ]"
          >
            <a-input-password
              v-model:value="formState.password2"
              placeholder="Confirm Password"
              size="large"
              :prefix="h(LockOutlined)"
            />
          </a-form-item>

          <a-collapse class="additional-info-collapse" ghost>
            <a-collapse-panel key="1" header="Additional Information">
              <a-form-item name="address">
                <a-input
                  v-model:value="formState.address"
                  placeholder="Address"
                  size="large"
                  :prefix="h(HomeOutlined)"
                />
              </a-form-item>

              <a-form-item name="city">
                <a-input
                  v-model:value="formState.city"
                  placeholder="City"
                  size="large"
                  :prefix="h(EnvironmentOutlined)"
                />
              </a-form-item>

              <a-form-item name="phone_number">
                <a-input
                  v-model:value="formState.phone_number"
                  placeholder="Phone Number"
                  size="large"
                  :prefix="h(PhoneOutlined)"
                />
              </a-form-item>
            </a-collapse-panel>
          </a-collapse>

          <a-form-item name="agreement">
            <a-checkbox v-model:checked="agreement">
              I agree to the <a href="#" @click.prevent="showTerms">Terms of Service</a> and
              <a href="#" @click.prevent="showPrivacy">Privacy Policy</a>
            </a-checkbox>
          </a-form-item>

          <a-form-item>
            <a-button type="primary" html-type="submit" :loading="isLoading" size="large" block>
              Create Account
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

        <div class="login-link">
          Already have an account? <router-link to="/login">Sign in</router-link>
        </div>
      </div>
    </div>

    <!-- Terms of Service Modal -->
    <a-modal v-model:visible="termsVisible" title="Terms of Service" @ok="termsVisible = false">
      <p>These are the terms of service for the Smart City Environmental Monitoring Platform.</p>
      <!-- Add more terms content here -->
    </a-modal>

    <!-- Privacy Policy Modal -->
    <a-modal v-model:visible="privacyVisible" title="Privacy Policy" @ok="privacyVisible = false">
      <p>This is the privacy policy for the Smart City Environmental Monitoring Platform.</p>
      <!-- Add more privacy content here -->
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { message } from 'ant-design-vue'
import {
  MailOutlined,
  LockOutlined,
  GoogleOutlined,
  UserOutlined,
  HomeOutlined,
  PhoneOutlined,
  EnvironmentOutlined,
  BarChartOutlined,
  NotificationOutlined,
} from '@ant-design/icons-vue'
import type { RegistrationData } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

// Form state
const formState = reactive<RegistrationData>({
  email: '',
  password: '',
  password2: '',
  first_name: '',
  last_name: '',
  role: 'citizen', // Default role
  address: '',
  city: '',
  phone_number: '',
})

const agreement = ref(false)
const termsVisible = ref(false)
const privacyVisible = ref(false)

// Computed properties
const isLoading = computed(() => authStore.isLoading)

// Password confirmation validator
const validatePassword = async (_rule: unknown, value: string) => {
  if (value !== formState.password) {
    return Promise.reject('The two passwords do not match')
  }
  return Promise.resolve()
}

// Methods
const handleSubmit = async () => {
  if (!agreement.value) {
    message.error('Please agree to the Terms of Service and Privacy Policy')
    return
  }

  try {
    const success = await authStore.register(formState)

    if (success) {
      message.success('Registration successful! You can now log in')
      router.push('/login')
    }
  } catch (error) {
    console.error('Registration error:', error)
  }
}

const showTerms = () => {
  termsVisible.value = true
}

const showPrivacy = () => {
  privacyVisible.value = true
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
  max-width: 480px;
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

.additional-info-collapse {
  margin-bottom: 1rem;
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

.login-link {
  text-align: center;
  margin-top: 1.5rem;
  color: rgba(0, 0, 0, 0.45);
  font-size: 0.9rem;
}

.login-link a {
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
