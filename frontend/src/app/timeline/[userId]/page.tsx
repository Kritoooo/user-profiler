'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { userApi, UserStats, TimelineItem, UserActivity } from '@/services/api'

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

interface StatCardProps {
  title: string
  value: string
}

const StatCard = ({ title, value }: StatCardProps) => (
  <div className="bg-white p-4 rounded-lg shadow">
    <h3 className="text-sm font-medium text-gray-500">{title}</h3>
    <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
  </div>
)

interface ActivityCardProps {
  activity: UserActivity
}

const ActivityCard = ({ activity }: ActivityCardProps) => (
  <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500">
    {/* Platform badge */}
    <span className="inline-block bg-gray-200 text-gray-700 px-2 py-1 rounded text-xs font-medium mb-2">
      {activity.platform.toUpperCase()}
    </span>
    
    {/* Title */}
    <h4 className="font-medium text-gray-900 mb-1">{activity.title}</h4>
    
    {/* Description */}
    {activity.description && (
      <p className="text-gray-600 text-sm mb-2">{activity.description}</p>
    )}
    
    {/* Footer with timestamp and URL */}
    <div className="flex justify-between items-center mt-3">
      <span className="text-gray-500 text-xs">
        {formatDateTime(activity.timestamp)}
      </span>
      
      {activity.url && (
        <a 
          href={activity.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800 text-xs"
        >
          View →
        </a>
      )}
    </div>
  </div>
)

export default function TimelinePage() {
  const params = useParams()
  const router = useRouter()
  const userId = params.userId as string

  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [timeline, setTimeline] = useState<TimelineItem[]>([])
  const [selectedPlatform, setSelectedPlatform] = useState('all')
  const [error, setError] = useState('')

  const getTopPlatform = (): string => {
    if (!stats || Object.keys(stats.platform_stats).length === 0) {
      return 'N/A'
    }
    
    return Object.entries(stats.platform_stats)
      .reduce((a, b) => a[1] > b[1] ? a : b)[0]
  }

  const getFilteredTimeline = (): TimelineItem[] => {
    if (selectedPlatform === 'all') {
      return timeline
    }
    
    return timeline.map(timelineItem => ({
      ...timelineItem,
      activities: timelineItem.activities.filter(activity => 
        activity.platform === selectedPlatform)
    })).filter(timelineItem => timelineItem.activities.length > 0)
  }

  const loadData = async () => {
    setLoading(true)
    setError('')
    
    try {
      // Load stats and timeline in parallel
      const [statsResponse, timelineResponse] = await Promise.all([
        userApi.getUserStats(userId),
        userApi.getUserTimeline(userId)
      ])
      
      setStats(statsResponse.data)
      setTimeline(timelineResponse.data)
      
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error loading timeline data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (userId) {
      loadData()
    }
  }, [userId])

  const refreshTimeline = () => {
    loadData()
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-gray-600 mt-4">Loading timeline data...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    )
  }

  const filteredTimeline = getFilteredTimeline()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Timeline for {userId}
          </h1>
          <p className="text-gray-600 mt-1">Digital footprint across platforms</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={refreshTimeline}
            disabled={loading}
            className={`bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 ${loading ? 'opacity-50' : ''}`}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
          <button
            onClick={() => router.push(`/profile/${userId}`)}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            View Profile
          </button>
        </div>
      </div>

      {/* Stats Summary */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard title="Total Activities" value={stats.total_activities.toString()} />
          <StatCard title="Platforms" value={Object.keys(stats.platform_stats).length.toString()} />
          <StatCard title="Top Platform" value={getTopPlatform()} />
          <StatCard 
            title="Last Activity" 
            value={stats.last_activity ? formatDate(stats.last_activity) : 'N/A'} 
          />
        </div>
      )}

      {/* Platform Filter */}
      {stats && Object.keys(stats.platform_stats).length > 0 && (
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Filter by Platform</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedPlatform('all')}
              className={`px-3 py-1 rounded-md text-sm ${
                selectedPlatform === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              All
            </button>
            
            {Object.keys(stats.platform_stats).map(platform => (
              <button
                key={platform}
                onClick={() => setSelectedPlatform(platform)}
                className={`px-3 py-1 rounded-md text-sm ${
                  selectedPlatform === platform
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {platform.charAt(0).toUpperCase() + platform.slice(1)}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Activity Timeline</h2>
        </div>
        
        <div className="p-6">
          {filteredTimeline.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No activities found for the selected platform.
            </p>
          ) : (
            filteredTimeline.map(timelineItem => (
              <div key={timelineItem.date} className="mb-8">
                {/* Date header */}
                <div className="flex items-center mb-4">
                  <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                    {formatDate(timelineItem.date)}
                  </div>
                  <span className="text-gray-500 ml-3 text-sm">
                    {timelineItem.activities.length} activities
                  </span>
                </div>
                
                {/* Activities list */}
                <div className="space-y-3 ml-4">
                  {timelineItem.activities.map(activity => (
                    <ActivityCard key={activity.id} activity={activity} />
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Empty state */}
      {timeline.length === 0 && !loading && (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No activities found</h3>
          <p className="text-gray-600">
            Try starting an analysis or check back later as data is being processed.
          </p>
        </div>
      )}
    </div>
  )
}