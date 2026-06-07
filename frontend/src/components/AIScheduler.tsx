import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../services/api'
import { Sparkles, Send } from 'lucide-react'

export default function AIScheduler() {
  const [prompt, setPrompt] = useState('')
  const queryClient = useQueryClient()

  const scheduleMutation = useMutation({
    mutationFn: (promptText: string) => 
      api.post('/ai/schedule-from-prompt', null, {
        params: { prompt: promptText }
      }),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-daily'] })
      setPrompt('')
      
      const task = response.data.task
      alert(`✨ Scheduled: "${task.title}"\n\n${response.data.ai_recommendation}`)
    },
    onError: (error: any) => {
      alert(`Error: ${error.response?.data?.detail || 'Failed to schedule'}`)
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (prompt.trim()) {
      scheduleMutation.mutate(prompt)
    }
  }

  const examplePrompts = [
    "Study for calculus exam for 2 hours before Friday",
    "Schedule 3 gym sessions this week in the morning",
    "Write essay due next Tuesday, need 4 hours total",
    "Practice coding problems 1 hour daily",
  ]

  return (
    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl shadow-sm p-6 border border-purple-200">
      <div className="flex items-center mb-4">
        <Sparkles className="w-6 h-6 text-purple-600 mr-3" />
        <div>
          <h2 className="text-xl font-semibold text-gray-900">AI Scheduler</h2>
          <p className="text-sm text-gray-600">Tell me what you need to do, I'll find the best time</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g., Study for CS midterm for 3 hours this week..."
            className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            disabled={scheduleMutation.isPending}
          />
          <button
            type="submit"
            disabled={!prompt.trim() || scheduleMutation.isPending}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {scheduleMutation.isPending ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-gray-600">Try:</span>
          {examplePrompts.map((example, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setPrompt(example)}
              className="text-xs px-3 py-1 bg-white border border-gray-300 rounded-full hover:border-purple-400 hover:text-purple-600 transition"
            >
              {example}
            </button>
          ))}
        </div>
      </form>
    </div>
  )
}

