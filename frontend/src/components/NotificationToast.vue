<template>
    <Transition enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0" leave-active-class="transition ease-in duration-100"
        leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="notification"
            class="fixed bottom-4 right-4 max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden">
            <div class="p-4">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <component :is="iconComponent" class="h-6 w-6" :class="iconClass" />
                    </div>
                    <div class="ml-3 w-0 flex-1 pt-0.5">
                        <p class="text-sm font-medium text-gray-900">
                            {{ notification.title }}
                        </p>
                        <p class="mt-1 text-sm text-gray-500">
                            {{ notification.message }}
                        </p>
                    </div>
                    <div class="ml-4 flex-shrink-0 flex">
                        <button @click="closeNotification"
                            class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500">
                            <XMarkIcon class="h-5 w-5" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Transition>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
    CheckCircleIcon,
    ExclamationCircleIcon,
    InformationCircleIcon,
    XMarkIcon
} from '@heroicons/vue/24/outline'

const notification = ref(null)

const iconComponent = computed(() => {
    const icons = {
        success: CheckCircleIcon,
        error: ExclamationCircleIcon,
        info: InformationCircleIcon
    }
    return icons[notification.value?.type] || InformationCircleIcon
})

const iconClass = computed(() => {
    const classes = {
        success: 'text-green-400',
        error: 'text-red-400',
        info: 'text-blue-400'
    }
    return classes[notification.value?.type] || 'text-blue-400'
})

function showNotification(type, title, message) {
    notification.value = { type, title, message }

    setTimeout(() => {
        notification.value = null
    }, 5000)
}

function closeNotification() {
    notification.value = null
}

// Expose method for use by other components
defineExpose({ showNotification })
</script>