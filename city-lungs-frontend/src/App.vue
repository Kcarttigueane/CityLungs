<template>
  <a-config-provider>
    <div class="app-container">
      <template v-if="isAuthenticated">
        <!-- Application layout when authenticated -->
        <a-layout style="min-height: 100vh">
          <a-layout-sider v-model:collapsed="collapsed" collapsible>
            <div class="logo">
              <h2 v-if="!collapsed" class="logo-text">City Lungs</h2>
              <h2 v-else class="logo-text">SC</h2>
            </div>
            <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline">
              <a-menu-item key="dashboard">
                <dashboard-outlined />
                <span>Dashboard</span>
                <router-link to="/dashboard" />
              </a-menu-item>
              <a-menu-item key="measurements">
                <line-chart-outlined />
                <span>Measurements</span>
                <router-link to="/measurements" />
              </a-menu-item>
              <a-menu-item key="predictions">
                <fund-projection-outlined />
                <span>Predictions</span>
                <router-link to="/predictions" />
              </a-menu-item>
              <a-menu-item key="alerts">
                <warning-outlined />
                <span>Alerts</span>
                <router-link to="/alerts" />
              </a-menu-item>
              <a-menu-item key="profile">
                <user-outlined />
                <span>Profile</span>
                <router-link to="/profile" />
              </a-menu-item>
            </a-menu>
          </a-layout-sider>
          <a-layout>
            <a-layout-header style="background: #fff; padding: 0">
              <div class="header-container">
                <div class="header-left">
                  <menu-unfold-outlined
                    v-if="collapsed"
                    class="trigger"
                    @click="() => (collapsed = !collapsed)"
                  />
                  <menu-fold-outlined
                    v-else
                    class="trigger"
                    @click="() => (collapsed = !collapsed)"
                  />
                </div>
                <div class="header-right">
                  <a-dropdown>
                    <a class="ant-dropdown-link" @click.prevent>
                      <a-avatar :size="32">
                        {{ avatarText }}
                      </a-avatar>
                      <span style="margin-left: 8px"
                        >{{ user?.first_name }} {{ user?.last_name }}</span
                      >
                      <down-outlined />
                    </a>
                    <template #overlay>
                      <a-menu>
                        <a-menu-item key="profile">
                          <router-link to="/profile">Profile</router-link>
                        </a-menu-item>
                        <a-menu-divider />
                        <a-menu-item key="logout" @click="handleLogout"> Logout </a-menu-item>
                      </a-menu>
                    </template>
                  </a-dropdown>
                  <a-badge :count="unreadAlertCount" :dot="unreadAlertCount > 0">
                    <a-button type="text" shape="circle" @click="showNotifications">
                      <template #icon><bell-outlined /></template>
                    </a-button>
                  </a-badge>
                </div>
              </div>
            </a-layout-header>
            <a-layout-content style="margin: 24px 16px 0">
              <div style="padding: 24px; background: #fff; min-height: 360px">
                <router-view />
              </div>
            </a-layout-content>
            <a-layout-footer style="text-align: center">
              City Lungs Environmental Monitoring Platform ©{{ new Date().getFullYear() }}
            </a-layout-footer>
          </a-layout>
        </a-layout>
      </template>
      <template v-else>
        <!-- Public pages layout when not authenticated -->
        <div class="auth-layout">
          <div class="auth-header">
            <router-link to="/" class="auth-logo">
              <h1>City Lungs</h1>
            </router-link>
          </div>
          <div class="auth-content">
            <router-view />
          </div>
          <div class="auth-footer">
            City Lungs Environmental Monitoring Platform ©{{ new Date().getFullYear() }}
          </div>
        </div>
      </template>

      <!-- Notifications drawer -->
      <a-drawer
        v-model:visible="notificationsVisible"
        title="Notifications"
        placement="right"
        width="400px"
      >
        <a-list itemLayout="horizontal" :dataSource="userAlerts" :loading="alertsLoading">
          <template v-if="userAlerts.length === 0">
            <a-empty description="No notifications" />
          </template>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <h3>Notifications</h3>
              <a-button type="link" @click="markAllAsRead" :disabled="!unreadAlertCount">
                Mark all as read
              </a-button>
            </div>
          </template>
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta :title="item.alert.title" :description="item.alert.description">
                <!-- <template #avatar>
                  <a-avatar
                    :style="{ backgroundColor: getAlertColor(item.alert.severity) }"
                    :icon="getAlertIcon(item.alert.alert_type)"
                  />
                </template> -->
              </a-list-item-meta>
              <template #extra>
                <a-button type="text" @click="markAsRead(item.id)" v-if="!item.is_read">
                  Mark as read
                </a-button>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </a-drawer>
    </div>
  </a-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  DashboardOutlined,
  LineChartOutlined,
  WarningOutlined,
  UserOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  BellOutlined,
  DownOutlined,
} from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useDataStore } from '@/stores/data'
// import type { Alert } from '@/types'

// State
const collapsed = ref<boolean>(false)
const selectedKeys = ref<string[]>(['dashboard'])
const notificationsVisible = ref<boolean>(false)
const alertsLoading = ref<boolean>(false)

// Stores
const authStore = useAuthStore()
const dataStore = useDataStore()
const route = useRoute()

// Computed properties
const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)
const userAlerts = computed(() => dataStore.userAlerts)
const unreadAlertCount = computed(() => dataStore.unreadUserAlerts.length)

const avatarText = computed(() => {
  if (user.value?.first_name && user.value.last_name) {
    return `${user.value.first_name[0]}${user.value.last_name[0]}`.toUpperCase()
  }
  return user.value?.email?.[0].toUpperCase() || '?'
})

// Route change handler to update selected menu item
watch(
  () => route.path,
  (path) => {
    const key = path.split('/')[1] || 'dashboard'
    selectedKeys.value = [key]
  },
)

// Methods
const handleLogout = () => {
  authStore.logout()
}

const showNotifications = async () => {
  notificationsVisible.value = true
  alertsLoading.value = true

  try {
    await dataStore.fetchUserAlerts()
  } catch (error) {
    console.error('Failed to fetch notifications:', error)
  } finally {
    alertsLoading.value = false
  }
}

const markAsRead = async (id: number) => {
  await dataStore.markAlertAsRead(id)
}

const markAllAsRead = async () => {
  await dataStore.markAllAlertsAsRead()
}

// const getAlertColor = (severity: Alert['severity']) => {
//   switch (severity) {
//     case 'low':
//       return '#52c41a'
//     case 'medium':
//       return '#faad14'
//     case 'high':
//       return '#fa8c16'
//     case 'critical':
//       return '#f5222d'
//     default:
//       return '#1890ff'
//   }
// }

// const getAlertIcon = (type: Alert['alert_type']) => {
//   switch (type) {
//     case 'pollution':
//       return <AlertOutlined />
//     case 'weather':
//       return <ThunderboltOutlined />
//     case 'traffic':
//       return <CarOutlined />
//     default:
//       return <WarningOutlined />
//   }
// }

// Initialize app
onMounted(async () => {
  // Update selected keys based on current route
  const path = route.path
  const key = path.split('/')[1] || 'dashboard'
  selectedKeys.value = [key]

  // Fetch user alerts if authenticated
  if (authStore.isAuthenticated) {
    await dataStore.fetchUserAlerts()
  }
})
</script>

<style scoped>
.app-container {
  height: 100%;
}

.logo {
  height: 32px;
  margin: 16px;
  text-align: center;
}

.logo-text {
  color: white;
  margin: 0;
  font-size: 18px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 100%;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: #1890ff;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.auth-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.auth-header {
  padding: 24px;
  text-align: center;
}

.auth-logo {
  text-decoration: none;
  color: inherit;
}

.auth-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.auth-footer {
  padding: 24px;
  text-align: center;
}
</style>
