'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { userApi } from '@/services/api'

interface RecentAnalysis {
  userId: string
  totalActivities: number
}

export default function Home() {
  const [userId, setUserId] = useState('')
  const [selectedPlatforms, setSelectedPlatforms] = useState(['github'])
  const [selectedSearchEngines, setSelectedSearchEngines] = useState(['google'])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('')
  const [recentAnalyses] = useState<RecentAnalysis[]>([])
  const router = useRouter()

  const handlePlatformChange = (platform: string, checked: boolean) => {
    if (checked) {
      setSelectedPlatforms(prev => [...prev.filter(p => p !== platform), platform])
    } else {
      setSelectedPlatforms(prev => prev.filter(p => p !== platform))
    }
  }

  const handleSearchEngineChange = (engine: string, checked: boolean) => {
    if (checked) {
      setSelectedSearchEngines(prev => [...prev.filter(e => e !== engine), engine])
    } else {
      setSelectedSearchEngines(prev => prev.filter(e => e !== engine))
    }
  }

  const showMessage = (text: string, type: 'success' | 'error') => {
    setMessage(text)
    setMessageType(type)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!userId.trim()) {
      showMessage('Please enter a user ID', 'error')
      return
    }
    
    setLoading(true)
    setMessage('')
    
    try {
      await userApi.crawlUser(
        userId.trim(),
        selectedPlatforms,
        selectedSearchEngines
      )
      
      showMessage(
        `Analysis started for ${userId}. This may take a few minutes.`,
        'success'
      )
      
      // Redirect to timeline after a short delay
      setTimeout(() => {
        router.push(`/timeline/${userId}`)
      }, 2000)
      
    } catch (error: any) {
      showMessage(
        error.response?.data?.detail || 'Error starting analysis',
        'error'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          User Digital Footprint Analyzer
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Track and analyze user activities across GitHub, Zhihu, Xiaohongshu, and more. 
          Generate comprehensive user profiles with AI-powered insights.
        </p>
      </div>

      {/* Search Form */}
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Start User Analysis
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                User ID
              </label>
              <input
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter GitHub username, Zhihu ID, etc."
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Platforms to Search
              </label>
              <div className="grid grid-cols-2 gap-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedPlatforms.includes('github')}
                    onChange={(e) => handlePlatformChange('github', e.target.checked)}
                    className="mr-2"
                  />
                  GitHub
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedPlatforms.includes('zhihu')}
                    onChange={(e) => handlePlatformChange('zhihu', e.target.checked)}
                    className="mr-2"
                  />
                  Zhihu
                </label>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Engines
              </label>
              <div className="grid grid-cols-2 gap-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedSearchEngines.includes('google')}
                    onChange={(e) => handleSearchEngineChange('google', e.target.checked)}
                    className="mr-2"
                  />
                  Google
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedSearchEngines.includes('bing')}
                    onChange={(e) => handleSearchEngineChange('bing', e.target.checked)}
                    className="mr-2"
                  />
                  Bing
                </label>
              </div>
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Starting Analysis...' : 'Start Analysis'}
            </button>
          </form>
          
          {message && (
            <div className={`mt-4 p-3 rounded-md ${
              messageType === 'success'
                ? 'bg-green-100 text-green-700 border border-green-200'
                : 'bg-red-100 text-red-700 border border-red-200'
            }`}>
              {message}
            </div>
          )}
        </div>
      </div>

      {/* Recent Analyses (if any) */}
      {recentAnalyses.length > 0 && (
        <div className="max-w-4xl mx-auto">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Analyses</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentAnalyses.map((analysis) => (
              <div
                key={analysis.userId}
                className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow"
              >
                <h3 className="font-medium text-gray-900">{analysis.userId}</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {analysis.totalActivities} activities found
                </p>
                <div className="flex space-x-2 mt-3">
                  <button
                    onClick={() => router.push(`/timeline/${analysis.userId}`)}
                    className="text-sm bg-blue-100 text-blue-700 px-2 py-1 rounded"
                  >
                    Timeline
                  </button>
                  <button
                    onClick={() => router.push(`/profile/${analysis.userId}`)}
                    className="text-sm bg-green-100 text-green-700 px-2 py-1 rounded"
                  >
                    Profile
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}