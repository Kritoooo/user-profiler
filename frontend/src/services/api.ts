import axios, { AxiosInstance, AxiosResponse } from 'axios'

// Type definitions
interface CrawlRequest {
  user_id: string
  platforms?: string[]
  search_engines?: string[]
}

interface UserActivity {
  id: string
  user_id: string
  platform: string
  activity_type: string
  title: string
  description?: string
  url?: string
  timestamp: string
  metadata?: Record<string, any>
}

interface UserProfile {
  user_id: string
  activity_summary: {
    total_activities: number
    platform_breakdown: Record<string, number>
    date_range?: {
      earliest: string
      latest: string
      span_days: number
    }
    activity_frequency?: Record<string, number>
  }
  generated_profile?: {
    interests: string[]
    skills: string[]
    personality_traits: string[]
    activity_patterns: string[]
    summary: string
  }
  created_at: string
  updated_at: string
}

interface UserStats {
  total_activities: number
  platform_stats: Record<string, number>
  last_activity: string | null
}

interface TimelineItem {
  date: string
  activities: UserActivity[]
}

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// Request interceptor
api.interceptors.request.use(
  config => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor  
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const userApi = {
  // Start crawling user data
  crawlUser(userId: string, platforms: string[] = ['github', 'zhihu'], searchEngines: string[] = ['google', 'bing']): Promise<AxiosResponse> {
    return api.post('/crawl', {
      user_id: userId,
      platforms,
      search_engines: searchEngines
    } as CrawlRequest)
  },

  // Get user activities
  getUserActivities(userId: string, platform: string | null = null, limit: number = 100): Promise<AxiosResponse<UserActivity[]>> {
    const params: any = { limit }
    if (platform) params.platform = platform
    
    return api.get(`/users/${userId}/activities`, { params })
  },

  // Get user timeline
  getUserTimeline(userId: string): Promise<AxiosResponse<TimelineItem[]>> {
    return api.get(`/users/${userId}/timeline`)
  },

  // Get user profile
  getUserProfile(userId: string): Promise<AxiosResponse<UserProfile>> {
    return api.get(`/users/${userId}/profile`)
  },

  // Generate user profile
  generateProfile(userId: string): Promise<AxiosResponse<UserProfile>> {
    return api.post(`/users/${userId}/profile/generate`)
  },

  // Get user statistics
  getUserStats(userId: string): Promise<AxiosResponse<UserStats>> {
    return api.get(`/users/${userId}/stats`)
  },

  // Health check
  healthCheck(): Promise<AxiosResponse> {
    return api.get('/health')
  },

  // Get recent logs
  getRecentLogs(lines: number = 100): Promise<AxiosResponse<string[]>> {
    return api.get(`/logs/recent?lines=${lines}`)
  },

  // Get log stream (EventSource)
  getLogStream(): EventSource {
    return new EventSource('/api/logs/stream')
  }
}

export default api
export type { UserActivity, UserProfile, UserStats, TimelineItem, CrawlRequest }