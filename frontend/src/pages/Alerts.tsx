import { useEffect, useState } from 'react'
import { api, AIAlert } from '../lib/api'
import { AlertTriangle, Info, AlertCircle, Check, X } from 'lucide-react'
import { format } from 'date-fns'

export default function Alerts() {
  const [alerts, setAlerts] = useState<AIAlert[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'unread' | 'resolved'>('all')

  useEffect(() => {
    loadAlerts()
    // Trigger AI evaluation on mount
    evaluateAI()
  }, [])

  const loadAlerts = async () => {
    setLoading(true)
    try {
      let url = '/ai/alerts'
      if (filter === 'unread') {
        url = '/ai/alerts/unread'
      } else if (filter === 'resolved') {
        url = '/ai/alerts?is_resolved=true'
      }
      const data = await api.get<AIAlert[]>(url)
      setAlerts(data)
    } catch (error) {
      console.error('Failed to load alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const evaluateAI = async () => {
    try {
      await api.post('/ai/evaluate')
      await loadAlerts()
    } catch (error) {
      console.error('Failed to evaluate AI rules:', error)
    }
  }

  const markAsRead = async (alertId: number) => {
    try {
      await api.put(`/ai/alerts/${alertId}`, { is_read: true })
      await loadAlerts()
    } catch (error) {
      console.error('Failed to mark alert as read:', error)
    }
  }

  const markAsResolved = async (alertId: number) => {
    try {
      await api.put(`/ai/alerts/${alertId}`, { is_resolved: true })
      await loadAlerts()
    } catch (error) {
      console.error('Failed to mark alert as resolved:', error)
    }
  }

  const deleteAlert = async (alertId: number) => {
    try {
      await api.delete(`/ai/alerts/${alertId}`)
      await loadAlerts()
    } catch (error) {
      console.error('Failed to delete alert:', error)
    }
  }

  useEffect(() => {
    loadAlerts()
  }, [filter])

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      case 'WARNING':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />
      case 'INFO':
        return <Info className="h-5 w-5 text-blue-600" />
      default:
        return <Info className="h-5 w-5 text-gray-600" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'border-red-200 bg-red-50'
      case 'WARNING':
        return 'border-yellow-200 bg-yellow-50'
      case 'INFO':
        return 'border-blue-200 bg-blue-50'
      default:
        return 'border-gray-200 bg-gray-50'
    }
  }

  if (loading) {
    return <div className="animate-pulse">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Alerts</h1>
          <p className="mt-1 text-sm text-gray-500">
            Smart recommendations and budget alerts
          </p>
        </div>
        <button
          onClick={evaluateAI}
          className="bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700"
        >
          Refresh Alerts
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('unread')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'unread'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Unread
          </button>
          <button
            onClick={() => setFilter('resolved')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              filter === 'resolved'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Resolved
          </button>
        </div>
      </div>

      {/* Alerts List */}
      {alerts.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No alerts found</p>
          <p className="text-sm text-gray-400 mt-2">
            AI will generate alerts based on your spending patterns and budget status
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`border rounded-lg p-6 ${getSeverityColor(alert.severity)} ${
                alert.is_read ? 'opacity-75' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  {getSeverityIcon(alert.severity)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {alert.title}
                      </h3>
                      {!alert.is_read && (
                        <span className="px-2 py-1 bg-primary-600 text-white text-xs rounded-full">
                          New
                        </span>
                      )}
                      {alert.is_resolved && (
                        <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">
                          Resolved
                        </span>
                      )}
                    </div>
                    <p className="text-gray-700 mb-2">{alert.message}</p>
                    <p className="text-xs text-gray-500">
                      {format(new Date(alert.created_at), 'MMM d, yyyy h:mm a')}
                    </p>
                  </div>
                </div>
                <div className="flex space-x-2 ml-4">
                  {!alert.is_read && (
                    <button
                      onClick={() => markAsRead(alert.id)}
                      className="p-2 text-gray-600 hover:text-gray-900 hover:bg-white rounded"
                      title="Mark as read"
                    >
                      <Check className="h-4 w-4" />
                    </button>
                  )}
                  {!alert.is_resolved && (
                    <button
                      onClick={() => markAsResolved(alert.id)}
                      className="p-2 text-gray-600 hover:text-gray-900 hover:bg-white rounded"
                      title="Mark as resolved"
                    >
                      <Check className="h-4 w-4" />
                    </button>
                  )}
                  <button
                    onClick={() => deleteAlert(alert.id)}
                    className="p-2 text-gray-600 hover:text-red-600 hover:bg-white rounded"
                    title="Delete"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
