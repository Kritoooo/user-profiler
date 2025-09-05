<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">
          Profile for {{ userId }}
        </h1>
        <p class="text-gray-600 mt-1">AI-generated user insights and analysis</p>
      </div>
      <div class="flex space-x-3">
        <button
          @click="generateProfile"
          :disabled="generating"
          class="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50"
        >
          {{ generating ? 'Generating...' : 'Generate Profile' }}
        </button>
        <router-link
          :to="`/timeline/${userId}`"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          View Timeline
        </router-link>
      </div>
    </div>

    <!-- Profile Content -->
    <div v-if="profile" class="space-y-6">
      <!-- Activity Summary -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Activity Summary</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">{{ profile.activity_summary.total_activities }}</div>
            <div class="text-sm text-gray-600">Total Activities</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">{{ Object.keys(profile.activity_summary.platform_breakdown).length }}</div>
            <div class="text-sm text-gray-600">Platforms</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-purple-600">{{ profile.activity_summary.date_range?.span_days || 0 }}</div>
            <div class="text-sm text-gray-600">Days of Activity</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-orange-600">{{ Object.keys(profile.activity_summary.activity_frequency || {}).length }}</div>
            <div class="text-sm text-gray-600">Active Months</div>
          </div>
        </div>

        <!-- Platform Breakdown Chart -->
        <div class="space-y-3">
          <h3 class="font-medium text-gray-900">Platform Distribution</h3>
          <div
            v-for="(count, platform) in profile.activity_summary.platform_breakdown"
            :key="platform"
            class="flex items-center"
          >
            <div class="w-24 text-sm text-gray-600">{{ platform }}</div>
            <div class="flex-1 bg-gray-200 rounded-full h-4 ml-3">
              <div
                class="bg-blue-600 h-4 rounded-full"
                :style="{ width: `${(count / profile.activity_summary.total_activities) * 100}%` }"
              ></div>
            </div>
            <div class="w-12 text-sm text-gray-800 text-right ml-3">{{ count }}</div>
          </div>
        </div>
      </div>

      <!-- AI Analysis -->
      <div v-if="profile.ai_analysis && !profile.ai_analysis.error" class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">AI Analysis</h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Personality Traits -->
          <div v-if="profile.ai_analysis.personality_traits">
            <h3 class="font-medium text-gray-900 mb-3">Personality Traits</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="trait in profile.ai_analysis.personality_traits"
                :key="trait"
                class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {{ trait }}
              </span>
            </div>
          </div>

          <!-- Interests -->
          <div v-if="profile.ai_analysis.interests">
            <h3 class="font-medium text-gray-900 mb-3">Interests</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="interest in profile.ai_analysis.interests"
                :key="interest"
                class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
              >
                {{ interest }}
              </span>
            </div>
          </div>

          <!-- Technical Skills -->
          <div v-if="profile.ai_analysis.technical_skills">
            <h3 class="font-medium text-gray-900 mb-3">Technical Skills</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="skill in profile.ai_analysis.technical_skills"
                :key="skill"
                class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
              >
                {{ skill }}
              </span>
            </div>
          </div>

          <!-- Content Themes -->
          <div v-if="profile.ai_analysis.content_themes">
            <h3 class="font-medium text-gray-900 mb-3">Content Themes</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="theme in profile.ai_analysis.content_themes"
                :key="theme"
                class="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm"
              >
                {{ theme }}
              </span>
            </div>
          </div>
        </div>

        <!-- Text Analysis -->
        <div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div v-if="profile.ai_analysis.activity_pattern">
            <h3 class="font-medium text-gray-900 mb-3">Activity Pattern</h3>
            <p class="text-gray-700 bg-gray-50 p-3 rounded">{{ profile.ai_analysis.activity_pattern }}</p>
          </div>

          <div v-if="profile.ai_analysis.social_presence">
            <h3 class="font-medium text-gray-900 mb-3">Social Presence</h3>
            <p class="text-gray-700 bg-gray-50 p-3 rounded">{{ profile.ai_analysis.social_presence }}</p>
          </div>

          <div v-if="profile.ai_analysis.engagement_style">
            <h3 class="font-medium text-gray-900 mb-3">Engagement Style</h3>
            <p class="text-gray-700 bg-gray-50 p-3 rounded">{{ profile.ai_analysis.engagement_style }}</p>
          </div>
        </div>
      </div>

      <!-- Timeline Highlights -->
      <div v-if="profile.timeline_highlights?.length > 0" class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Timeline Highlights</h2>
        
        <div class="space-y-4">
          <div
            v-for="highlight in profile.timeline_highlights"
            :key="highlight.date + highlight.platform"
            class="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg"
          >
            <div class="text-2xl">{{ getPlatformIcon(highlight.platform) }}</div>
            <div class="flex-1">
              <div class="font-medium text-gray-900">{{ highlight.title }}</div>
              <div class="text-sm text-gray-600">{{ highlight.platform }} • {{ formatDate(highlight.date) }}</div>
            </div>
            <div class="text-sm font-medium text-blue-600">{{ highlight.type }}</div>
          </div>
        </div>
      </div>

      <!-- Digital Footprint -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Digital Footprint</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 class="font-medium text-gray-900 mb-3">Active Platforms</h3>
            <ul class="space-y-1">
              <li
                v-for="platform in profile.digital_footprint.platforms_active"
                :key="platform"
                class="text-gray-700 flex items-center"
              >
                <span class="mr-2">{{ getPlatformIcon(platform) }}</span>
                {{ platform }}
              </li>
            </ul>
          </div>

          <div>
            <h3 class="font-medium text-gray-900 mb-3">Content Types</h3>
            <ul class="space-y-1">
              <li
                v-for="(count, type) in profile.digital_footprint.content_types"
                :key="type"
                class="text-gray-700 flex justify-between"
              >
                <span>{{ type }}</span>
                <span class="font-medium">{{ count }}</span>
              </li>
            </ul>
          </div>

          <div>
            <h3 class="font-medium text-gray-900 mb-3">Profile Stats</h3>
            <div class="text-sm text-gray-600">
              <p>Generated: {{ formatDate(profile.generated_at) }}</p>
              <p>User ID: {{ profile.user_id }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Profile State -->
    <div v-else-if="!loading && !generating" class="text-center py-12">
      <div class="text-gray-400 text-6xl mb-4">👤</div>
      <h3 class="text-lg font-medium text-gray-900">No profile generated yet</h3>
      <p class="text-gray-600 mt-1 mb-4">
        Generate an AI-powered profile based on collected activities.
      </p>
      <button
        @click="generateProfile"
        class="bg-purple-600 text-white px-6 py-3 rounded-md hover:bg-purple-700"
      >
        Generate Profile
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading || generating" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
      <p class="text-gray-600 mt-4">
        {{ generating ? 'Generating profile with AI...' : 'Loading profile...' }}
      </p>
    </div>
  </div>
</template>

<script>
import { userApi } from '../services/api'

export default {
  name: 'Profile',
  props: ['userId'],
  data() {
    return {
      profile: null,
      loading: false,
      generating: false
    }
  },
  
  async mounted() {
    await this.loadProfile()
  },
  
  methods: {
    async loadProfile() {
      this.loading = true
      try {
        const response = await userApi.getUserProfile(this.userId)
        this.profile = response.data.profile_data
      } catch (error) {
        if (error.response?.status !== 404) {
          console.error('Error loading profile:', error)
        }
      } finally {
        this.loading = false
      }
    },
    
    async generateProfile() {
      this.generating = true
      try {
        await userApi.generateProfile(this.userId)
        
        // Wait a moment then try to load the profile
        setTimeout(async () => {
          await this.loadProfile()
          this.generating = false
        }, 5000)
        
      } catch (error) {
        this.generating = false
        console.error('Error generating profile:', error)
        alert(error.response?.data?.detail || 'Error generating profile')
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
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
    }
  }
}
</script>