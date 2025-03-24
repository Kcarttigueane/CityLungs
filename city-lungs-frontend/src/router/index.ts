// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { message } from 'ant-design-vue'

// Import view components
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ForgotPasswordView from '@/views/ForgotPasswordView.vue'
import ProfileView from '@/views/ProfileView.vue'
import DashboardView from '@/views/DashboardView.vue'
// import MeasurementsView from '@/views/MeasurementsView.vue'
// import PredictionsView from '@/views/PredictionsView.vue'
// import AlertsView from '@/views/AlertsView.vue'
// import PasswordResetView from '@/views/PasswordResetView.vue'
// import PasswordResetConfirmView from '@/views/PasswordResetConfirmView.vue'
// import NotFoundView from '@/views/NotFoundView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { guestOnly: true },
    },
    {
      path: '/forgot-password',
      name: 'forgotPassword',
      component: ForgotPasswordView,
      meta: { guestOnly: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true },
    },
    // {
    //   path: '/measurements',
    //   name: 'measurements',
    //   component: MeasurementsView,
    //   meta: { requiresAuth: true },
    // },
    // {
    //   path: '/predictions',
    //   name: 'predictions',
    //   component: PredictionsView,
    //   meta: { requiresAuth: true },
    // },
    // {
    //   path: '/alerts',
    //   name: 'alerts',
    //   component: AlertsView,
    //   meta: { requiresAuth: true },
    // },
    // {
    //   path: '/password-reset',
    //   name: 'passwordReset',
    //   component: PasswordResetView,
    //   meta: { guestOnly: true },
    // },
    // {
    //   path: '/password-reset-confirm/:uid/:token',
    //   name: 'passwordResetConfirm',
    //   component: PasswordResetConfirmView,
    //   meta: { guestOnly: true },
    // },
    // {
    //   path: '/:pathMatch(.*)*',
    //   name: 'not-found',
    //   component: NotFoundView,
    // },
  ],
})

// Navigation guard
// router.beforeEach((to, from, next) => {
//   const authStore = useAuthStore()
//   const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
//   const guestOnly = to.matched.some((record) => record.meta.guestOnly)

//   // Check if route requires authentication
//   if (requiresAuth && !authStore.isAuthenticated) {
//     message.warning('Please log in to access this page')
//     next({ name: 'login', query: { redirect: to.fullPath } })
//   }
//   // Check if route is for guests only (like login page)
//   else if (guestOnly && authStore.isAuthenticated) {
//     next({ name: 'dashboard' })
//   }
//   // All good, proceed
//   else {
//     next()
//   }
// })

export default router
