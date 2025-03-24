<template>
  <div class="profile-container">
    <a-page-header title="Profile" />
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" tab="Personal Information">
        <a-form
          :model="profileForm"
          name="profile-form"
          @finish="handleProfileSubmit"
          :label-col="{ span: 6 }"
          :wrapper-col="{ span: 14 }"
          class="profile-form"
        >
          <a-form-item label="Email" name="email">
            <a-input v-model:value="profileForm.email" disabled />
          </a-form-item>

          <a-form-item
            label="First Name"
            name="first_name"
            :rules="[{ required: true, message: 'First name is required!' }]"
          >
            <a-input v-model:value="profileForm.first_name" />
          </a-form-item>

          <a-form-item
            label="Last Name"
            name="last_name"
            :rules="[{ required: true, message: 'Last name is required!' }]"
          >
            <a-input v-model:value="profileForm.last_name" />
          </a-form-item>

          <a-form-item label="Address" name="address">
            <a-input v-model:value="profileForm.address" />
          </a-form-item>

          <a-form-item label="City" name="city">
            <a-input v-model:value="profileForm.city" />
          </a-form-item>

          <a-form-item label="Phone Number" name="phone_number">
            <a-input v-model:value="profileForm.phone_number" />
          </a-form-item>

          <a-form-item label="Role" name="role">
            <a-tag :color="profileForm.role === 'admin' ? 'volcano' : 'green'">
              {{ profileForm.role === 'admin' ? 'Administrator' : 'Citizen' }}
            </a-tag>
          </a-form-item>

          <a-divider />

          <a-form-item label="Email Notifications" name="email_notifications">
            <a-switch
              v-model:checked="profileForm.profile.email_notifications"
              checked-children="On"
              un-checked-children="Off"
            />
          </a-form-item>

          <a-form-item label="Push Notifications" name="push_notifications">
            <a-switch
              v-model:checked="profileForm.profile.push_notifications"
              checked-children="On"
              un-checked-children="Off"
            />
          </a-form-item>

          <a-form-item label="Default View" name="default_view">
            <a-select v-model:value="profileForm.profile.default_view">
              <a-select-option value="pollution">Pollution</a-select-option>
              <a-select-option value="weather">Weather</a-select-option>
              <a-select-option value="traffic">Traffic</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="Alert Threshold" name="notification_threshold">
            <a-slider
              v-model:value="profileForm.profile.notification_threshold"
              :min="0"
              :max="100"
              :marks="{
                0: 'Low',
                25: '25%',
                50: '50%',
                75: '75%',
                100: 'High',
              }"
            />
          </a-form-item>

          <a-form-item :wrapper-col="{ offset: 6, span: 14 }">
            <a-button type="primary" html-type="submit" :loading="isLoading">
              Save Changes
            </a-button>
          </a-form-item>
        </a-form>
      </a-tab-pane>

      <a-tab-pane key="2" tab="Change Password">
        <a-form
          :model="passwordForm"
          name="password-form"
          @finish="handlePasswordSubmit"
          :label-col="{ span: 6 }"
          :wrapper-col="{ span: 14 }"
          class="password-form"
        >
          <a-form-item
            label="Current Password"
            name="old_password"
            :rules="[{ required: true, message: 'Please input your current password!' }]"
          >
            <a-input-password v-model:value="passwordForm.old_password" />
          </a-form-item>

          <a-form-item
            label="New Password"
            name="new_password"
            :rules="[
              { required: true, message: 'Please input your new password!' },
              { min: 8, message: 'Password must be at least 8 characters!' },
            ]"
          >
            <a-input-password v-model:value="passwordForm.new_password" />
          </a-form-item>

          <a-form-item
            label="Confirm New Password"
            name="new_password2"
            :rules="[
              { required: true, message: 'Please confirm your new password!' },
              { validator: validatePassword },
            ]"
          >
            <a-input-password v-model:value="passwordForm.new_password2" />
          </a-form-item>

          <a-form-item :wrapper-col="{ offset: 6, span: 14 }">
            <a-button type="primary" html-type="submit" :loading="passwordLoading">
              Change Password
            </a-button>
          </a-form-item>
        </a-form>
      </a-tab-pane>

      <a-tab-pane key="3" tab="Account Activity">
        <a-descriptions title="Account Information" bordered>
          <a-descriptions-item label="User ID">{{ user?.id }}</a-descriptions-item>
          <a-descriptions-item label="Registration Date">{{
            formatDate(user?.date_joined)
          }}</a-descriptions-item>
          <a-descriptions-item label="Last Login">{{
            formatDate(user?.last_login)
          }}</a-descriptions-item>
          <a-descriptions-item label="Account Type">
            <a-tag :color="user?.role === 'admin' ? 'volcano' : 'green'">
              {{ user?.role === 'admin' ? 'Administrator' : 'Citizen' }}
            </a-tag>
          </a-descriptions-item>
        </a-descriptions>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { User, PasswordChangeData } from '@/types'
import { message } from 'ant-design-vue'

const authStore = useAuthStore()

// Form states
const profileForm = reactive<User>({
  id: 0,
  email: '',
  first_name: '',
  last_name: '',
  role: 'citizen',
  address: '',
  city: '',
  phone_number: '',
  profile: {
    email_notifications: true,
    push_notifications: true,
    default_view: 'pollution',
    notification_threshold: 75,
  },
})

const passwordForm = reactive<PasswordChangeData>({
  old_password: '',
  new_password: '',
  new_password2: '',
})

// Computed properties
const user = computed(() => authStore.user)
const isLoading = computed(() => authStore.isLoading)
const passwordLoading = ref(false)

// Password confirmation validator
const validatePassword = async (_rule: unknown, value: string) => {
  if (value !== passwordForm.new_password) {
    return Promise.reject('The two passwords do not match!')
  }
  return Promise.resolve()
}

// Methods
const handleProfileSubmit = async () => {
  // Create update data object without the id which is not editable
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { id, ...updateData } = profileForm

  const success = await authStore.updateProfile(updateData)
  if (success) {
    message.success('Profile updated successfully')
  }
}

const handlePasswordSubmit = async () => {
  passwordLoading.value = true
  try {
    const success = await authStore.changePassword(passwordForm)
    if (success) {
      message.success('Password changed successfully')
      // Reset form
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.new_password2 = ''
    }
  } finally {
    passwordLoading.value = false
  }
}

// Format date for display
const formatDate = (dateString?: string) => {
  if (!dateString) return 'N/A'

  return new Date(dateString).toLocaleString()
}

// Initialize form with user data
onMounted(() => {
  if (user.value) {
    // Copy user data to form state
    Object.assign(profileForm, user.value)

    // Ensure profile object exists with defaults if not present
    if (!profileForm.profile) {
      profileForm.profile = {
        email_notifications: true,
        push_notifications: true,
        default_view: 'pollution',
        notification_threshold: 75,
      }
    }
  }
})
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
}

.profile-form,
.password-form {
  max-width: 600px;
  margin-top: 24px;
}
</style>
