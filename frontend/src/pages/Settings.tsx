import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { usersApi } from '../services/api'
import { User, Clock, Moon, Dumbbell, Heart } from 'lucide-react'

export default function Settings() {
  const { data: preferences } = useQuery({
    queryKey: ['preferences'],
    queryFn: () => usersApi.getPreferences().then((res) => res.data),
  })

  const updatePreferencesMutation = useMutation({
    mutationFn: (data: any) => usersApi.updatePreferences(data),
  })

  const [formData, setFormData] = useState(preferences || {})

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updatePreferencesMutation.mutate(formData)
  }

  const handleChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }))
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Manage your preferences and schedule optimization</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Circadian Rhythm */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <Moon className="w-6 h-6 text-primary-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">Circadian Rhythm</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Wake Time
              </label>
              <input
                type="time"
                value={formData.wake_time || '07:00'}
                onChange={(e) => handleChange('wake_time', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sleep Time
              </label>
              <input
                type="time"
                value={formData.sleep_time || '23:00'}
                onChange={(e) => handleChange('sleep_time', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Peak Focus Time
              </label>
              <select
                value={formData.peak_focus_time || 'morning'}
                onChange={(e) => handleChange('peak_focus_time', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="morning">Morning (6-12 AM)</option>
                <option value="afternoon">Afternoon (12-5 PM)</option>
                <option value="evening">Evening (5-9 PM)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Study Preferences */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <Clock className="w-6 h-6 text-primary-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">Study Preferences</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Study Session Duration (minutes)
              </label>
              <input
                type="number"
                value={formData.study_session_duration || 50}
                onChange={(e) => handleChange('study_session_duration', parseInt(e.target.value))}
                min="15"
                max="180"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Break Duration (minutes)
              </label>
              <input
                type="number"
                value={formData.break_duration || 10}
                onChange={(e) => handleChange('break_duration', parseInt(e.target.value))}
                min="5"
                max="30"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        {/* Fitness Preferences */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <Dumbbell className="w-6 h-6 text-primary-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">Fitness Goals</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Gym Frequency (times per week)
              </label>
              <input
                type="number"
                value={formData.gym_frequency || 3}
                onChange={(e) => handleChange('gym_frequency', parseInt(e.target.value))}
                min="0"
                max="7"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Workout Duration (minutes)
              </label>
              <input
                type="number"
                value={formData.workout_duration || 60}
                onChange={(e) => handleChange('workout_duration', parseInt(e.target.value))}
                min="15"
                max="180"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Workout Time
              </label>
              <select
                value={formData.preferred_workout_time || 'morning'}
                onChange={(e) => handleChange('preferred_workout_time', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="morning">Morning</option>
                <option value="afternoon">Afternoon</option>
                <option value="evening">Evening</option>
              </select>
            </div>
          </div>
        </div>

        {/* Schedule Preferences */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center mb-4">
            <Heart className="w-6 h-6 text-primary-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900">Schedule Optimization</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Auto-reschedule</p>
                <p className="text-sm text-gray-600">
                  Let AI automatically reschedule tasks based on priorities
                </p>
              </div>
              <input
                type="checkbox"
                checked={formData.auto_reschedule !== false}
                onChange={(e) => handleChange('auto_reschedule', e.target.checked)}
                className="w-6 h-6 text-primary-600 rounded focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Buffer Time Between Events (minutes)
              </label>
              <input
                type="number"
                value={formData.buffer_time || 15}
                onChange={(e) => handleChange('buffer_time', parseInt(e.target.value))}
                min="0"
                max="60"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={updatePreferencesMutation.isPending}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
          >
            {updatePreferencesMutation.isPending ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>

        {updatePreferencesMutation.isSuccess && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            Preferences saved successfully!
          </div>
        )}
      </form>
    </div>
  )
}

