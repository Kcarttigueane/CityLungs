<template>
    <div class="admin-view container mx-auto px-4 py-8">
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p class="mt-2 text-gray-600">System configuration and management</p>
        </div>

        <!-- Alert Configurations -->
        <div class="mb-8">
            <div class="bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                    <h2 class="text-xl font-semibold">Alert Configurations</h2>
                    <button @click="showAddConfig = true" class="btn btn-primary text-sm">
                        Add Configuration
                    </button>
                </div>

                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Parameter
                                </th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Threshold
                                </th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Severity
                                </th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Status
                                </th>
                                <th
                                    class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            <tr v-for="config in alertConfigs" :key="config.id">
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {{ config.parameter.toUpperCase() }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {{ config.threshold_value }}
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span :class="getSeverityBadgeClass(config.severity)">
                                        {{ config.severity }}
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <ToggleSwitch :modelValue="config.is_enabled"
                                        @update:modelValue="toggleConfig(config)" />
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <button @click="editConfig(config)"
                                        class="text-primary-600 hover:text-primary-900 mr-3">
                                        Edit
                                    </button>
                                    <button @click="deleteConfig(config.id)" class="text-red-600 hover:text-red-900">
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- System Status -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold mb-4">Data Collection Status</h3>
                <div class="space-y-3">
                    <StatusIndicator label="OpenWeather API" :status="systemStatus.openweather"
                        :lastUpdate="systemStatus.openweatherLastUpdate" />
                    <StatusIndicator label="OpenAQ API" :status="systemStatus.openaq"
                        :lastUpdate="systemStatus.openaqLastUpdate" />
                    <StatusIndicator label="Database Connection" :status="systemStatus.database"
                        :lastUpdate="systemStatus.databaseLastUpdate" />
                </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-lg font-semibold mb-4">Model Performance</h3>
                <div class="space-y-3">
                    <div v-for="model in modelMetrics" :key="model.name" class="border-b pb-3">
                        <div class="flex justify-between items-center">
                            <span class="font-medium">{{ model.name }}</span>
                            <span class="text-sm text-gray-500">MAE: {{ model.mae }}</span>
                        </div>
                        <div class="mt-1 text-xs text-gray-400">
                            Last trained: {{ model.lastTrained }}
                        </div>
                    </div>
                </div>
                <button @click="triggerTraining" class="btn btn-secondary w-full mt-4" :disabled="trainingInProgress">
                    {{ trainingInProgress ? 'Training in Progress...' : 'Retrain Models' }}
                </button>
            </div>
        </div>

        <!-- Add/Edit Configuration Modal -->
        <TransitionRoot :show="showAddConfig" as="template">
            <Dialog @close="showAddConfig = false" class="relative z-50">
                <div class="fixed inset-0 bg-black/30" aria-hidden="true" />

                <div class="fixed inset-0 flex items-center justify-center p-4">
                    <DialogPanel class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
                        <DialogTitle class="text-lg font-semibold mb-4">
                            {{ editingConfig ? 'Edit' : 'Add' }} Alert Configuration
                        </DialogTitle>

                        <form @submit.prevent="saveConfig" class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">
                                    Parameter
                                </label>
                                <select v-model="configForm.parameter" class="form-input w-full" required>
                                    <option value="">Select parameter</option>
                                    <option value="pm25">PM2.5</option>
                                    <option value="pm10">PM10</option>
                                    <option value="no2">NO2</option>
                                    <option value="so2">SO2</option>
                                    <option value="co">CO</option>
                                    <option value="o3">O3</option>
                                    <option value="aqi">AQI</option>
                                </select>
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">
                                    Threshold Value
                                </label>
                                <input v-model.number="configForm.threshold_value" type="number" step="0.01"
                                    class="form-input w-full" required />
                            </div>

                            <div>
                                <label class="block text-sm font-medium text-gray-700 mb-1">
                                    Severity
                                </label>
                                <select v-model="configForm.severity" class="form-input w-full" required>
                                    <option value="">Select severity</option>
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                    <option value="critical">Critical</option>
                                </select>
                            </div>

                            <div class="flex justify-end space-x-3 mt-6">
                                <button type="button" @click="showAddConfig = false" class="btn btn-secondary">
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    {{ editingConfig ? 'Update' : 'Create' }}
                                </button>
                            </div>
                        </form>
                    </DialogPanel>
                </div>
            </Dialog>
        </TransitionRoot>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot } from '@headlessui/vue'
import api from '@/services/api'
import ToggleSwitch from '@/components/ToggleSwitch.vue'
import StatusIndicator from '@/components/StatusIndicator.vue'

const alertConfigs = ref([])
const showAddConfig = ref(false)
const editingConfig = ref(null)
const trainingInProgress = ref(false)

const configForm = reactive({
    parameter: '',
    threshold_value: 0,
    severity: '',
    is_enabled: true
})

const systemStatus = ref({
    openweather: 'online',
    openweatherLastUpdate: '2 minutes ago',
    openaq: 'online',
    openaqLastUpdate: '5 minutes ago',
    database: 'online',
    databaseLastUpdate: 'Just now'
})

const modelMetrics = ref([
    { name: 'Random Forest', mae: 8.2, lastTrained: '2 days ago' },
    { name: 'XGBoost', mae: 7.8, lastTrained: '2 days ago' }
])

function getSeverityBadgeClass(severity) {
    const classes = {
        low: 'px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800',
        medium: 'px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800',
        high: 'px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800',
        critical: 'px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800'
    }
    return classes[severity] || classes.medium
}

async function loadAlertConfigs() {
    try {
        const response = await api.get('/alert-configs/')
        alertConfigs.value = response.data.results || []
    } catch (error) {
        console.error('Failed to load alert configs:', error)
    }
}

async function saveConfig() {
    try {
        if (editingConfig.value) {
            await api.put(`/alert-configs/${editingConfig.value.id}/`, configForm)
        } else {
            await api.post('/alert-configs/', configForm)
        }

        showAddConfig.value = false
        editingConfig.value = null
        resetForm()
        await loadAlertConfigs()
    } catch (error) {
        console.error('Failed to save config:', error)
    }
}

async function toggleConfig(config) {
    try {
        await api.patch(`/alert-configs/${config.id}/`, {
            is_enabled: !config.is_enabled
        })
        await loadAlertConfigs()
    } catch (error) {
        console.error('Failed to toggle config:', error)
    }
}

async function deleteConfig(id) {
    if (!confirm('Are you sure you want to delete this configuration?')) return

    try {
        await api.delete(`/alert-configs/${id}/`)
        await loadAlertConfigs()
    } catch (error) {
        console.error('Failed to delete config:', error)
    }
}

function editConfig(config) {
    editingConfig.value = config
    Object.assign(configForm, {
        parameter: config.parameter,
        threshold_value: config.threshold_value,
        severity: config.severity,
        is_enabled: config.is_enabled
    })
    showAddConfig.value = true
}

function resetForm() {
    Object.assign(configForm, {
        parameter: '',
        threshold_value: 0,
        severity: '',
        is_enabled: true
    })
}

async function triggerTraining() {
    trainingInProgress.value = true
    try {
        const response = await api.post('http://localhost:5000/train', {
            location: 'all'
        })
        console.log('Training started:', response.data)

        // Simulate training time
        setTimeout(() => {
            trainingInProgress.value = false
        }, 30000)
    } catch (error) {
        console.error('Failed to trigger training:', error)
        trainingInProgress.value = false
    }
}

onMounted(() => {
    loadAlertConfigs()
})
</script>