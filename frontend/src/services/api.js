import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// Request interceptor
api.interceptors.request.use(
  config => {
    console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`)
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
  crawlUser(userId, platforms = ['github', 'zhihu'], searchEngines = ['google', 'bing']) {
    return api.post('/crawl', {
      user_id: userId,
      platforms,
      search_engines: searchEngines
    })
  },

  // Get user activities
  getUserActivities(userId, platform = null, limit = 100) {
    const params = { limit }
    if (platform) params.platform = platform
    
    return api.get(`/users/${userId}/activities`, { params })
  },

  // Get user timeline
  getUserTimeline(userId) {
    return api.get(`/users/${userId}/timeline`)
  },

  // Get user profile
  getUserProfile(userId) {
    return api.get(`/users/${userId}/profile`)
  },

  // Generate user profile
  generateProfile(userId) {
    return api.post(`/users/${userId}/profile/generate`)
  },

  // Get user statistics
  getUserStats(userId) {
    return api.get(`/users/${userId}/stats`)
  },

  // Health check
  healthCheck() {
    return api.get('/health')
  },

  // Get recent logs
  getRecentLogs(lines = 100) {
    return api.get(`/logs/recent?lines=${lines}`)
  },

  // Get log stream (EventSource)
  getLogStream() {
    return new EventSource('/api/logs/stream')
  }
}

export default api