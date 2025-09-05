<template>
  <div class="space-y-6">
    <!-- Hero Section -->
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">
        User Digital Footprint Analyzer
      </h1>
      <p class="text-xl text-gray-600 max-w-3xl mx-auto">
        Track and analyze user activities across GitHub, Zhihu, Xiaohongshu, and more. 
        Generate comprehensive user profiles with AI-powered insights.
      </p>
    </div>

    <!-- Search Form -->
    <div class="max-w-2xl mx-auto">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">
          Start User Analysis
        </h2>
        
        <form @submit.prevent="startAnalysis" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              User ID
            </label>
            <input
              v-model="userId"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter GitHub username, Zhihu ID, etc."
              required
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Platforms to Search
            </label>
            <div class="grid grid-cols-2 gap-2">
              <label class="flex items-center">
                <input
                  type="checkbox"
                  v-model="selectedPlatforms"
                  value="github"
                  class="mr-2"
                >
                GitHub
              </label>
              <label class="flex items-center">
                <input
                  type="checkbox"
                  v-model="selectedPlatforms"
                  value="zhihu"
                  class="mr-2"
                >
                Zhihu
              </label>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Search Engines
            </label>
            <div class="grid grid-cols-2 gap-2">
              <label class="flex items-center">
                <input
                  type="checkbox"
                  v-model="selectedSearchEngines"
                  value="google"
                  class="mr-2"
                >
                Google
              </label>
              <label class="flex items-center">
                <input
                  type="checkbox"
                  v-model="selectedSearchEngines"
                  value="bing"
                  class="mr-2"
                >
                Bing
              </label>
            </div>
          </div>
          
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {{ loading ? 'Starting Analysis...' : 'Start Analysis' }}
          </button>
        </form>
        
        <div v-if="message" class="mt-4 p-3 rounded-md" :class="messageClass">
          {{ message }}
        </div>
      </div>
    </div>

    <!-- Recent Analyses (if any) -->
    <div v-if="recentAnalyses.length > 0" class="max-w-4xl mx-auto">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Recent Analyses</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="analysis in recentAnalyses"
          :key="analysis.userId"
          class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow"
        >
          <h3 class="font-medium text-gray-900">{{ analysis.userId }}</h3>
          <p class="text-sm text-gray-600 mt-1">
            {{ analysis.totalActivities }} activities found
          </p>
          <div class="flex space-x-2 mt-3">
            <router-link
              :to="`/timeline/${analysis.userId}`"
              class="text-sm bg-blue-100 text-blue-700 px-2 py-1 rounded"
            >
              Timeline
            </router-link>
            <router-link
              :to="`/profile/${analysis.userId}`"
              class="text-sm bg-green-100 text-green-700 px-2 py-1 rounded"
            >
              Profile
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { userApi } from '../services/api'

export default {
  name: 'Home',
  data() {
    return {
      userId: '',
      selectedPlatforms: ['github'],
      selectedSearchEngines: ['google'],
      loading: false,
      message: '',
      messageClass: '',
      recentAnalyses: []
    }
  },
  methods: {
    async startAnalysis() {
      if (!this.userId.trim()) {
        this.showMessage('Please enter a user ID', 'error')
        return
      }
      
      this.loading = true
      this.message = ''
      
      try {
        const response = await userApi.crawlUser(
          this.userId.trim(),
          this.selectedPlatforms,
          this.selectedSearchEngines
        )
        
        this.showMessage(
          `Analysis started for ${this.userId}. This may take a few minutes.`,
          'success'
        )
        
        // Redirect to timeline after a short delay
        setTimeout(() => {
          this.$router.push(`/timeline/${this.userId}`)
        }, 2000)
        
      } catch (error) {
        this.showMessage(
          error.response?.data?.detail || 'Error starting analysis',
          'error'
        )
      } finally {
        this.loading = false
      }
    },
    
    showMessage(text, type) {
      this.message = text
      this.messageClass = type === 'success' 
        ? 'bg-green-100 text-green-700 border border-green-200'
        : 'bg-red-100 text-red-700 border border-red-200'
    }
  }
}
</script>