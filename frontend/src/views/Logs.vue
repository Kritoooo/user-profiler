<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">System Logs</h1>
        <p class="text-gray-600 mt-1">Real-time system activity and debugging information</p>
      </div>
      <div class="flex space-x-3">
        <button
          @click="toggleAutoRefresh"
          :class="autoRefresh ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 hover:bg-gray-700'"
          class="text-white px-4 py-2 rounded-md"
        >
          {{ autoRefresh ? '⏸️ Stop Auto-refresh' : '▶️ Start Auto-refresh' }}
        </button>
        <button
          @click="clearLogs"
          class="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
        >
          🗑️ Clear
        </button>
        <button
          @click="refreshLogs"
          :disabled="loading"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? '🔄 Loading...' : '🔄 Refresh' }}
        </button>
      </div>
    </div>

    <!-- Controls -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap gap-4 items-center">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Log Level</label>
          <select
            v-model="selectedLevel"
            @change="filterLogs"
            class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Levels</option>
            <option value="DEBUG">Debug</option>
            <option value="INFO">Info</option>
            <option value="WARNING">Warning</option>
            <option value="ERROR">Error</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Filter User</label>
          <input
            v-model="userFilter"
            @input="filterLogs"
            placeholder="Enter user ID"
            class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            @input="filterLogs"
            placeholder="Search in logs..."
            class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
        </div>

        <div class="flex items-end">
          <button
            @click="exportLogs"
            class="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
          >
            💾 Export
          </button>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500">Total Logs</h3>
        <p class="text-2xl font-bold text-blue-600 mt-1">{{ totalLogs }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500">Errors</h3>
        <p class="text-2xl font-bold text-red-600 mt-1">{{ errorCount }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500">Warnings</h3>
        <p class="text-2xl font-bold text-yellow-600 mt-1">{{ warningCount }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500">Last Update</h3>
        <p class="text-sm font-medium text-gray-900 mt-1">{{ lastUpdate }}</p>
      </div>
    </div>

    <!-- Log Display -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold text-gray-900">
            Log Entries ({{ filteredLogs.length }})
          </h2>
          <div class="text-sm text-gray-600">
            {{ autoRefresh ? '🔴 Live' : '⏸️ Paused' }}
          </div>
        </div>
      </div>

      <div 
        ref="logContainer"
        class="h-96 overflow-y-auto bg-gray-900 text-green-400 font-mono text-sm p-4"
        style="font-family: 'Courier New', monospace;"
      >
        <div
          v-for="(log, index) in filteredLogs"
          :key="index"
          :class="getLogLineClass(log)"
          class="py-1 px-2 rounded hover:bg-gray-800 cursor-pointer"
          @click="selectLog(log)"
        >
          <span class="text-gray-500">{{ formatTimestamp(log.timestamp) }}</span>
          <span :class="getLevelClass(log.level)" class="ml-2 font-bold">{{ log.level }}</span>
          <span class="ml-2 text-white">{{ log.message }}</span>
          <span v-if="log.user_id" class="ml-2 text-blue-400">[user:{{ log.user_id }}]</span>
          <span v-if="log.platform" class="ml-1 text-purple-400">[{{ log.platform }}]</span>
        </div>
        
        <div v-if="filteredLogs.length === 0" class="text-center text-gray-500 py-8">
          No logs match your current filters
        </div>
      </div>
    </div>

    <!-- Selected Log Detail -->
    <div v-if="selectedLog" class="bg-white rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Log Detail</h3>
      <div class="bg-gray-50 rounded-md p-4">
        <pre class="text-sm text-gray-800 whitespace-pre-wrap">{{ JSON.stringify(selectedLog, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import { userApi } from '../services/api'

export default {
  name: 'Logs',
  data() {
    return {
      logs: [],
      filteredLogs: [],
      selectedLog: null,
      loading: false,
      autoRefresh: false,
      refreshInterval: null,
      selectedLevel: 'all',
      userFilter: '',
      searchQuery: '',
      lastUpdate: 'Never'
    }
  },
  
  computed: {
    totalLogs() {
      return this.logs.length
    },
    
    errorCount() {
      return this.logs.filter(log => log.level === 'ERROR' || log.level === 'CRITICAL').length
    },
    
    warningCount() {
      return this.logs.filter(log => log.level === 'WARNING').length
    }
  },
  
  async mounted() {
    await this.refreshLogs()
  },
  
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  
  methods: {
    async refreshLogs() {
      this.loading = true
      try {
        const response = await userApi.getRecentLogs(500)
        this.logs = response.data.logs.map(log => ({
          ...log,
          level: this.extractLevel(log.message),
          user_id: this.extractUserId(log.message),
          platform: this.extractPlatform(log.message)
        }))
        
        this.filterLogs()
        this.lastUpdate = new Date().toLocaleTimeString()
        
        // Auto-scroll to bottom
        this.$nextTick(() => {
          this.scrollToBottom()
        })
        
      } catch (error) {
        console.error('Error fetching logs:', error)
      } finally {
        this.loading = false
      }
    },
    
    filterLogs() {
      let filtered = [...this.logs]
      
      // Filter by level
      if (this.selectedLevel !== 'all') {
        filtered = filtered.filter(log => log.level === this.selectedLevel)
      }
      
      // Filter by user
      if (this.userFilter) {
        filtered = filtered.filter(log => 
          log.user_id && log.user_id.toLowerCase().includes(this.userFilter.toLowerCase())
        )
      }
      
      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(log =>
          log.message.toLowerCase().includes(query)
        )
      }
      
      this.filteredLogs = filtered
    },
    
    toggleAutoRefresh() {
      this.autoRefresh = !this.autoRefresh
      
      if (this.autoRefresh) {
        this.refreshInterval = setInterval(() => {
          this.refreshLogs()
        }, 2000) // Refresh every 2 seconds
      } else if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    },
    
    clearLogs() {
      this.logs = []
      this.filteredLogs = []
      this.selectedLog = null
    },
    
    selectLog(log) {
      this.selectedLog = log
    },
    
    scrollToBottom() {
      const container = this.$refs.logContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    exportLogs() {
      const data = JSON.stringify(this.filteredLogs, null, 2)
      const blob = new Blob([data], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      
      const a = document.createElement('a')
      a.href = url
      a.download = `user-profiler-logs-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    },
    
    formatTimestamp(timestamp) {
      return new Date(timestamp).toLocaleTimeString()
    },
    
    getLevelClass(level) {
      const classes = {
        'DEBUG': 'text-cyan-400',
        'INFO': 'text-green-400', 
        'WARNING': 'text-yellow-400',
        'ERROR': 'text-red-400',
        'CRITICAL': 'text-red-600'
      }
      return classes[level] || 'text-gray-400'
    },
    
    getLogLineClass(log) {
      if (log.level === 'ERROR' || log.level === 'CRITICAL') {
        return 'bg-red-900 bg-opacity-20 border-l-4 border-red-500'
      } else if (log.level === 'WARNING') {
        return 'bg-yellow-900 bg-opacity-20 border-l-4 border-yellow-500'
      }
      return ''
    },
    
    extractLevel(message) {
      const match = message.match(/\|\s*(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s*\|/)
      return match ? match[1] : 'INFO'
    },
    
    extractUserId(message) {
      const match = message.match(/\[user:([^\]]+)\]/)
      return match ? match[1] : null
    },
    
    extractPlatform(message) {
      const match = message.match(/\[([a-zA-Z_]+)\]/)
      return match && !match[1].startsWith('user:') ? match[1] : null
    }
  }
}
</script>