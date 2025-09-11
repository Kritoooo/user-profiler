'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { userApi, UserProfile } from '@/services/api'

export default function ProfilePage() {
  const params = useParams()
  const router = useRouter()
  const userId = params.userId as string

  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [generating, setGenerating] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadProfile = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await userApi.getUserProfile(userId)
      setProfile(response.data)
    } catch (error: any) {
      if (error.response?.status === 404) {
        setError('Profile not found. You may need to generate it first.')
      } else {
        setError(error.response?.data?.detail || 'Error loading profile')
      }
    } finally {
      setLoading(false)
    }
  }

  const generateProfile = async () => {
    setGenerating(true)
    
    try {
      const response = await userApi.generateProfile(userId)
      setProfile(response.data)
      setError('')
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error generating profile')
    } finally {
      setGenerating(false)
    }
  }

  useEffect(() => {
    if (userId) {
      loadProfile()
    }
  }, [userId])

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="text-gray-600 mt-4">Loading profile...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Profile for {userId}
          </h1>
          <p className="text-gray-600 mt-1">AI-generated user insights and analysis</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={generateProfile}
            disabled={generating}
            className={`bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 ${generating ? 'opacity-50' : ''}`}
          >
            {generating ? 'Generating...' : 'Generate Profile'}
          </button>
          <button
            onClick={() => router.push(`/timeline/${userId}`)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            View Timeline
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Profile Content */}
      {profile ? (
        <div className="space-y-6">
          {/* Activity Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Activity Summary</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {profile.activity_summary.total_activities}
                </div>
                <div className="text-sm text-gray-600">Total Activities</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {Object.keys(profile.activity_summary.platform_breakdown).length}
                </div>
                <div className="text-sm text-gray-600">Platforms</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {profile.activity_summary.date_range?.span_days || 0}
                </div>
                <div className="text-sm text-gray-600">Days of Activity</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {Object.keys(profile.activity_summary.activity_frequency || {}).length}
                </div>
                <div className="text-sm text-gray-600">Active Months</div>
              </div>
            </div>

            {/* Platform Breakdown */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-3">Platform Breakdown</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {Object.entries(profile.activity_summary.platform_breakdown).map(([platform, count]) => (
                  <div key={platform} className="bg-gray-50 rounded-lg p-3">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-700 capitalize">{platform}</span>
                      <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                        {count} activities
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Activity Frequency */}
            {profile.activity_summary.activity_frequency && 
             Object.keys(profile.activity_summary.activity_frequency).length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Monthly Activity</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                  {Object.entries(profile.activity_summary.activity_frequency).map(([month, count]) => (
                    <div key={month} className="bg-gray-50 rounded-lg p-3 text-center">
                      <div className="text-sm font-medium text-gray-700">{month}</div>
                      <div className="text-lg font-bold text-blue-600">{count}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Generated Profile Section */}
          {profile.generated_profile && (
            <div className="space-y-6">
              {/* Profile Summary */}
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">AI-Generated Profile</h2>
                <div className="prose max-w-none">
                  <p className="text-gray-700 leading-relaxed">
                    {profile.generated_profile.summary}
                  </p>
                </div>
              </div>

              {/* Profile Details */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Interests */}
                {profile.generated_profile.interests && profile.generated_profile.interests.length > 0 && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      🎯 Interests & Topics
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {profile.generated_profile.interests.map((interest, index) => (
                        <span
                          key={index}
                          className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                        >
                          {interest}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Skills */}
                {profile.generated_profile.skills && profile.generated_profile.skills.length > 0 && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      💡 Skills & Technologies
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {profile.generated_profile.skills.map((skill, index) => (
                        <span
                          key={index}
                          className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Personality Traits */}
                {profile.generated_profile.personality_traits && profile.generated_profile.personality_traits.length > 0 && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      🎭 Personality Traits
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {profile.generated_profile.personality_traits.map((trait, index) => (
                        <span
                          key={index}
                          className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm"
                        >
                          {trait}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Activity Patterns */}
                {profile.generated_profile.activity_patterns && profile.generated_profile.activity_patterns.length > 0 && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      📊 Activity Patterns
                    </h3>
                    <ul className="space-y-2">
                      {profile.generated_profile.activity_patterns.map((pattern, index) => (
                        <li key={index} className="flex items-start">
                          <span className="flex-shrink-0 w-2 h-2 bg-orange-400 rounded-full mt-2 mr-3"></span>
                          <span className="text-gray-700 text-sm">{pattern}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Profile Metadata */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex justify-between items-center text-sm text-gray-600">
              <span>
                Profile created: {new Date(profile.created_at).toLocaleDateString()}
              </span>
              <span>
                Last updated: {new Date(profile.updated_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
      ) : !error && (
        <div className="text-center py-12">
          <div className="max-w-md mx-auto">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No profile available</h3>
            <p className="text-gray-600 mb-4">
              Generate an AI-powered profile to get insights about this user's digital footprint.
            </p>
            <button
              onClick={generateProfile}
              disabled={generating}
              className={`bg-purple-600 text-white px-6 py-3 rounded-md hover:bg-purple-700 ${generating ? 'opacity-50' : ''}`}
            >
              {generating ? 'Generating Profile...' : 'Generate Profile'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}