<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          Timeline for {{ userId }}
        </h1>
        <p class="text-gray-600 mt-1">Digital footprint across platforms</p>
      </div>
      <div class="flex space-x-3">
        <button
          @click="refreshTimeline"
          :disabled="loading"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
        <router-link
          :to="`/profile/${userId}`"
          class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
        >
          View Profile
        </router-link>
      </div>
    </div>

    <!-- Stats Summary -->
    <div v-if="stats" class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500">Total Activities</h3>
        <p class="text-2xl font-bold text-gray-900 mt-1">{{ stats.total_activities }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500">Platforms</h3>
        <p class="text-2xl font-bold text-gray-900 mt-1">{{ Object.keys(stats.platform_stats).length }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500">Top Platform</h3>
        <p class="text-lg font-bold text-gray-900 mt-1">{{ topPlatform }}</p>
      </div>
      <div class="bg-white p-4 rounded-lg shadow">
        <h3 class="text-sm font-medium text-gray-500">Last Activity</h3>
        <p class="text-sm font-medium text-gray-900 mt-1">
          {{ stats.last_activity ? formatDate(stats.last_activity) : 'N/A' }}
        </p>
      </div>
    </div>

    <!-- Platform Filter -->
    <div class="bg-white p-4 rounded-lg shadow">
      <h3 class="text-lg font-semibold text-gray-900 mb-3">Filter by Platform</h3>
      <div class="flex flex-wrap gap-2">
        <button
          @click="selectedPlatform = null"
          :class="platformButtonClass(null)"
        >
          All
        </button>
        <button
          v-for="platform in availablePlatforms"
          :key="platform"
          @click="selectedPlatform = platform"
          :class="platformButtonClass(platform)"
        >
          {{ platform }} ({{ platformCounts[platform] }})
        </button>
      </div>
    </div>

    <!-- Timeline -->
    <div v-if="filteredTimeline.length > 0" class="space-y-6">
      <div
        v-for="day in filteredTimeline"
        :key="day.date"
        class="bg-white rounded-lg shadow overflow-hidden"
      >
        <!-- Date Header -->
        <div class="bg-gray-50 px-6 py-3 border-b">
          <h2 class="text-lg font-semibold text-gray-900">
            {{ formatDate(day.date) }}
          </h2>
          <p class="text-sm text-gray-600">{{ day.activities.length }} activities</p>
        </div>

        <!-- Activities -->
        <div class="divide-y divide-gray-200">
          <div
            v-for="activity in day.activities"
            :key="activity.id"
            class="p-6 hover:bg-gray-50"
          >
            <div class="flex items-start space-x-4">
              <!-- Platform Icon/Badge -->
              <div :class="getPlatformBadgeClass(activity.platform)">
                {{ getPlatformIcon(activity.platform) }}
              </div>

              <!-- Activity Content -->
              <div class="flex-1">
                <div class="flex items-center justify-between">
                  <h3 class="text-lg font-medium text-gray-900">
                    {{ activity.title || 'Untitled Activity' }}
                  </h3>
                  <span class="text-sm text-gray-500">{{ activity.time }}</span>
                </div>

                <p class="text-gray-600 mt-1" v-if="activity.content_preview">
                  {{ activity.content_preview }}
                </p>

                <!-- Extracted Data Preview -->
                <div v-if="activity.extracted_data" class="mt-3">
                  <div class="bg-gray-100 rounded-md p-3">
                    <h4 class="text-sm font-medium text-gray-700 mb-2">Extracted Information</h4>
                    <div class="grid grid-cols-2 gap-2 text-sm">
                      <div v-for="(value, key) in getDisplayData(activity.extracted_data)" :key="key">
                        <span class="font-medium text-gray-600">{{ formatKey(key) }}:</span>
                        <span class="text-gray-800 ml-1">{{ formatValue(value) }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- URL Link -->
                <div class="mt-3">
                  <a
                    :href="activity.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    View Original →
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading" class="text-center py-12">
      <div class="text-gray-400 text-6xl mb-4">📭</div>
      <h3 class="text-lg font-medium text-gray-900">No activities found</h3>
      <p class="text-gray-600 mt-1">
        Try starting a new analysis or check back later.
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="text-gray-600 mt-4">Loading timeline data...</p>
    </div>
  </div>
</template>

<script>
import { userApi } from '../services/api'

export default {
  name: 'Timeline',
  props: ['userId'],
  data() {
    return {
      timeline: [],
      stats: null,
      selectedPlatform: null,
      loading: false
    }
  },
  computed: {
    availablePlatforms() {
      if (!this.stats) return []
      return Object.keys(this.stats.platform_stats)
    },
    
    platformCounts() {
      return this.stats?.platform_stats || {}
    },
    
    topPlatform() {
      if (!this.stats?.platform_stats) return 'N/A'
      const platforms = this.stats.platform_stats
      return Object.keys(platforms).reduce((a, b) => 
        platforms[a] > platforms[b] ? a : b
      )
    },
    
    filteredTimeline() {
      if (!this.selectedPlatform) return this.timeline
      
      return this.timeline.map(day => ({
        ...day,
        activities: day.activities.filter(activity => 
          activity.platform === this.selectedPlatform
        )
      })).filter(day => day.activities.length > 0)
    }
  },
  
  async mounted() {
    await this.loadTimeline()
    await this.loadStats()
  },
  
  methods: {
    async loadTimeline() {
      this.loading = true
      try {
        const response = await userApi.getUserTimeline(this.userId)
        this.timeline = response.data.timeline
      } catch (error) {
        console.error('Error loading timeline:', error)
      } finally {
        this.loading = false
      }
    },
    
    async loadStats() {
      try {
        const response = await userApi.getUserStats(this.userId)
        this.stats = response.data
      } catch (error) {
        console.error('Error loading stats:', error)
      }
    },
    
    async refreshTimeline() {
      await this.loadTimeline()
      await this.loadStats()
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    
    getPlatformIcon(platform) {
      const icons = {
        'github': '🐙',
        'zhihu': '🔍',
        'search_google': '🔎',
        'search_bing': '🔍',
        'search_baidu': '🔍'
      }
      return icons[platform] || '📄'
    },
    
    getPlatformBadgeClass(platform) {
      const baseClass = 'w-12 h-12 rounded-full flex items-center justify-center text-white font-medium text-sm'
      const colors = {
        'github': 'bg-gray-800',
        'zhihu': 'bg-blue-600',
        'search_google': 'bg-red-500',
        'search_bing': 'bg-green-500',
        'search_baidu': 'bg-purple-500'
      }
      return `${baseClass} ${colors[platform] || 'bg-gray-500'}`
    },
    
    platformButtonClass(platform) {
      const baseClass = 'px-3 py-1 rounded-full text-sm font-medium transition-colors'
      const isSelected = this.selectedPlatform === platform
      return isSelected
        ? `${baseClass} bg-blue-600 text-white`
        : `${baseClass} bg-gray-200 text-gray-700 hover:bg-gray-300`
    },
    
    getDisplayData(extractedData) {
      // Show only the most relevant fields
      const relevantFields = ['username', 'display_name', 'bio', 'description', 'followers', 'following', 'repositories_count', 'activity_type']
      const filtered = {}
      
      relevantFields.forEach(field => {
        if (extractedData[field] !== undefined && extractedData[field] !== null && extractedData[field] !== '') {
          filtered[field] = extractedData[field]
        }
      })
      
      return filtered
    },
    
    formatKey(key) {
      return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    
    formatValue(value) {
      if (typeof value === 'object') {
        return JSON.stringify(value)
      }
      return String(value)
    }
  }
}
</script>