import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '../services/api'
import { Calendar, CheckCircle, Clock, TrendingUp } from 'lucide-react'
import { format } from 'date-fns'
import AIScheduler from '../components/AIScheduler'

export default function Dashboard() {
  const { data: dailyData, isLoading } = useQuery({
    queryKey: ['dashboard-daily'],
    queryFn: () => dashboardApi.daily().then((res) => res.data),
  })

  const { data: insights } = useQuery({
    queryKey: ['dashboard-insights'],
    queryFn: () => dashboardApi.insights().then((res) => res.data),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const metrics = dailyData?.metrics || {}
  const events = dailyData?.events || []
  const tasks = dailyData?.tasks || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          {format(new Date(), 'EEEE, MMMM d, yyyy')}
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Events Today</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{metrics.total_events || 0}</p>
            </div>
            <Calendar className="w-10 h-10 text-primary-500" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Tasks Due</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{metrics.total_tasks || 0}</p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Scheduled Hours</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{metrics.scheduled_hours || 0}h</p>
            </div>
            <Clock className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Productivity Score</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{insights?.productivity_score || '-'}</p>
            </div>
            <TrendingUp className="w-10 h-10 text-purple-500" />
          </div>
        </div>
      </div>

      {/* AI Scheduler */}
      <AIScheduler />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Today's Events */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Today's Events</h2>
          
          {events.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No events scheduled for today</p>
          ) : (
            <div className="space-y-3">
              {events.map((event: any) => (
                <div
                  key={event.id}
                  className="flex items-center p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{event.title}</h3>
                    <p className="text-sm text-gray-600">
                      {format(new Date(event.start_time), 'h:mm a')} -{' '}
                      {format(new Date(event.end_time), 'h:mm a')}
                    </p>
                    {event.location && (
                      <p className="text-sm text-gray-500">{event.location}</p>
                    )}
                  </div>
                  <span className="px-3 py-1 bg-primary-100 text-primary-700 text-xs font-medium rounded-full">
                    {event.type}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Today's Tasks */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Tasks Due Today</h2>
          
          {tasks.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No tasks due today</p>
          ) : (
            <div className="space-y-3">
              {tasks.map((task: any) => (
                <div
                  key={task.id}
                  className="flex items-center p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{task.title}</h3>
                    {task.estimated_duration && (
                      <p className="text-sm text-gray-600">
                        ~{task.estimated_duration} minutes
                      </p>
                    )}
                    {task.optimal_time && (
                      <p className="text-sm text-gray-500">
                        Best time: {task.optimal_time}
                      </p>
                    )}
                  </div>
                  <span
                    className={`px-3 py-1 text-xs font-medium rounded-full ${
                      task.priority === 'urgent'
                        ? 'bg-red-100 text-red-700'
                        : task.priority === 'high'
                        ? 'bg-orange-100 text-orange-700'
                        : 'bg-blue-100 text-blue-700'
                    }`}
                  >
                    {task.priority}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* AI Insights */}
      {insights && (
        <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl shadow-sm p-6 border border-primary-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">AI Insights</h2>
          
          <div className="space-y-3">
            {insights.insights?.map((insight: string, index: number) => (
              <div key={index} className="flex items-start">
                <TrendingUp className="w-5 h-5 text-primary-600 mt-0.5 mr-3 flex-shrink-0" />
                <p className="text-gray-700">{insight}</p>
              </div>
            ))}
          </div>

          {insights.recommendations && insights.recommendations.length > 0 && (
            <div className="mt-4 pt-4 border-t border-primary-200">
              <h3 className="font-semibold text-gray-900 mb-2">Recommendations</h3>
              <ul className="space-y-2">
                {insights.recommendations.map((rec: string, index: number) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start">
                    <span className="text-primary-600 mr-2">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

