'use client'

import { useState, useEffect, useRef } from 'react'
import { userApi } from '@/services/api'

export default function LogsPage() {
  const [logs, setLogs] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [error, setError] = useState('')
  const logsEndRef = useRef<HTMLDivElement>(null)
  const eventSourceRef = useRef<EventSource | null>(null)

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadLogs = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await userApi.getRecentLogs(100)
      // Ensure response.data is an array
      setLogs(response.data)
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error loading logs')
      setLogs([]) // Reset to empty array on error
    } finally {
      setLoading(false)
    }
  }

  const startLogStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    try {
      eventSourceRef.current = userApi.getLogStream()
      
      eventSourceRef.current.onmessage = (event) => {
        const newLog = event.data
        setLogs(prevLogs => [...prevLogs, newLog])
        if (autoRefresh) {
          setTimeout(scrollToBottom, 100)
        }
      }
      
      eventSourceRef.current.onerror = (error) => {
        console.error('EventSource failed:', error)
        setError('Lost connection to log stream')
        setAutoRefresh(false)
      }
    } catch (error) {
      console.error('Failed to start log stream:', error)
      setError('Failed to start live log stream')
      setAutoRefresh(false)
    }
  }

  const stopLogStream = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
  }

  const handleAutoRefreshToggle = () => {
    if (autoRefresh) {
      setAutoRefresh(false)
      stopLogStream()
    } else {
      setAutoRefresh(true)
      startLogStream()
    }
  }

  const clearLogs = () => {
    setLogs([])
  }

  const refreshLogs = () => {
    loadLogs()
  }

  useEffect(() => {
    loadLogs()
    
    return () => {
      stopLogStream()
    }
  }, [])

  useEffect(() => {
    if (autoRefresh && logs.length > 0) {
      scrollToBottom()
    }
  }, [logs, autoRefresh])

  const formatLogLine = (logLine: string, index: number) => {
    // Simple log line formatting - you can enhance this based on your log format
    const timestamp = new Date().toISOString().slice(11, 19)
    const isError = logLine.toLowerCase().includes('error') || logLine.toLowerCase().includes('failed')
    const isWarning = logLine.toLowerCase().includes('warning') || logLine.toLowerCase().includes('warn')
    const isInfo = logLine.toLowerCase().includes('info') || logLine.toLowerCase().includes('success')
    
    let colorClass = 'text-gray-700'
    if (isError) colorClass = 'text-red-600'
    else if (isWarning) colorClass = 'text-yellow-600'
    else if (isInfo) colorClass = 'text-green-600'

    return (
      <div key={index} className={`font-mono text-sm py-1 ${colorClass}`}>
        <span className="text-gray-500 mr-2">[{String(index + 1).padStart(4, '0')}]</span>
        {logLine}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Logs</h1>
          <p className="text-gray-600 mt-1">Real-time application logs and events</p>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={clearLogs}
            className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
          >
            Clear
          </button>
          <button
            onClick={refreshLogs}
            disabled={loading}
            className={`bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 ${loading ? 'opacity-50' : ''}`}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
          <button
            onClick={handleAutoRefreshToggle}
            className={`px-4 py-2 rounded-md ${
              autoRefresh
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {autoRefresh ? 'Stop Live' : 'Start Live'}
          </button>
        </div>
      </div>

      {/* Status */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center">
          <div className={`w-3 h-3 rounded-full mr-2 ${autoRefresh ? 'bg-green-500' : 'bg-gray-400'}`}></div>
          <span className="text-sm text-gray-600">
            {autoRefresh ? 'Live updates active' : 'Live updates off'}
          </span>
        </div>
        <div className="text-sm text-gray-600">
          {logs.length} log entries
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Logs Container */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-900">Log Output</h2>
        </div>
        
        <div className="p-4">
          {loading && logs.length === 0 ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <p className="text-gray-600 mt-2">Loading logs...</p>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600">No logs available</p>
            </div>
          ) : (
            <div 
              className="bg-gray-900 rounded-lg p-4 max-h-96 overflow-y-auto"
              style={{ fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace' }}
            >
              {Array.isArray(logs) && logs.map((logLine, index) => (
                <div key={index} className="text-green-400 text-sm py-0.5">
                  <span className="text-gray-500 mr-2">[{String(index + 1).padStart(4, '0')}]</span>
                  {logLine}
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 mb-2">💡 Tips</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Click "Start Live" to see real-time log updates</li>
          <li>• Use "Refresh" to manually reload recent logs</li>
          <li>• "Clear" will remove all displayed logs from view</li>
          <li>• Logs automatically scroll to bottom when live updates are active</li>
        </ul>
      </div>
    </div>
  )
}