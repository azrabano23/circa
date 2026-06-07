import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tasksApi } from '../services/api'
import { Plus, CheckCircle, Circle, Trash2 } from 'lucide-react'
import { format } from 'date-fns'

export default function Tasks() {
  const [filter, setFilter] = useState<string>('all')
  const queryClient = useQueryClient()

  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.list().then((res) => res.data),
  })

  const updateTaskMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => tasksApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  const deleteTaskMutation = useMutation({
    mutationFn: (id: number) => tasksApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  const handleToggleComplete = (task: any) => {
    const newStatus = task.status === 'completed' ? 'todo' : 'completed'
    updateTaskMutation.mutate({
      id: task.id,
      data: { status: newStatus },
    })
  }

  const handleDeleteTask = (id: number) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      deleteTaskMutation.mutate(id)
    }
  }

  const filteredTasks = tasks?.filter((task: any) => {
    if (filter === 'all') return true
    if (filter === 'completed') return task.status === 'completed'
    if (filter === 'active') return task.status !== 'completed'
    return true
  }) || []

  const sortedTasks = [...filteredTasks].sort((a: any, b: any) => {
    // Sort by priority and due date
    const priorityOrder: Record<string, number> = { urgent: 0, high: 1, medium: 2, low: 3 }
    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority]
    
    if (priorityDiff !== 0) return priorityDiff
    
    if (a.due_date && b.due_date) {
      return new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
    }
    
    return 0
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading tasks...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
        <button className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition">
          <Plus className="w-5 h-5 mr-2" />
          New Task
        </button>
      </div>

      {/* Filters */}
      <div className="flex space-x-2">
        {['all', 'active', 'completed'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === f
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Tasks List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        {sortedTasks.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-500">No tasks found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {sortedTasks.map((task: any) => (
              <div
                key={task.id}
                className="p-4 hover:bg-gray-50 transition flex items-center space-x-4"
              >
                {/* Checkbox */}
                <button
                  onClick={() => handleToggleComplete(task)}
                  className="flex-shrink-0"
                >
                  {task.status === 'completed' ? (
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  ) : (
                    <Circle className="w-6 h-6 text-gray-400 hover:text-gray-600" />
                  )}
                </button>

                {/* Task Info */}
                <div className="flex-1 min-w-0">
                  <h3
                    className={`font-medium ${
                      task.status === 'completed'
                        ? 'text-gray-400 line-through'
                        : 'text-gray-900'
                    }`}
                  >
                    {task.title}
                  </h3>
                  {task.description && (
                    <p className="text-sm text-gray-600 truncate">{task.description}</p>
                  )}
                  <div className="flex items-center space-x-4 mt-1">
                    {task.due_date && (
                      <span className="text-xs text-gray-500">
                        Due: {format(new Date(task.due_date), 'MMM d, yyyy')}
                      </span>
                    )}
                    {task.estimated_duration && (
                      <span className="text-xs text-gray-500">
                        {task.estimated_duration}min
                      </span>
                    )}
                    {task.ai_extracted && (
                      <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded">
                        AI
                      </span>
                    )}
                  </div>
                </div>

                {/* Priority Badge */}
                <span
                  className={`flex-shrink-0 px-3 py-1 text-xs font-medium rounded-full ${
                    task.priority === 'urgent'
                      ? 'bg-red-100 text-red-700'
                      : task.priority === 'high'
                      ? 'bg-orange-100 text-orange-700'
                      : task.priority === 'medium'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}
                >
                  {task.priority}
                </span>

                {/* Delete Button */}
                <button
                  onClick={() => handleDeleteTask(task.id)}
                  className="flex-shrink-0 p-2 text-gray-400 hover:text-red-600 transition"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

