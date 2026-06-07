import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { manualImportApi } from '../services/api'
import { X, Upload, FileText, Sparkles } from 'lucide-react'

interface CanvasManualImportProps {
  onClose: () => void
}

export default function CanvasManualImport({ onClose }: CanvasManualImportProps) {
  const [pastedText, setPastedText] = useState('')
  const [activeTab, setActiveTab] = useState<'paste' | 'help'>('paste')
  const queryClient = useQueryClient()

  const pasteMutation = useMutation({
    mutationFn: (text: string) => manualImportApi.pasteCanvas(text),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard-daily'] })
      alert(`✅ Imported ${response.data.imported_count} assignments!\n\nCheck your Tasks page to see them.`)
      onClose()
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to import. Make sure you pasted valid assignment text.'
      alert(`❌ Import failed: ${message}`)
    }
  })

  const handlePaste = () => {
    if (!pastedText.trim()) {
      alert('Please paste some text first!')
      return
    }
    pasteMutation.mutate(pastedText)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-500 to-red-500 p-6 text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Upload className="w-8 h-8" />
              <div>
                <h2 className="text-2xl font-bold">Import Canvas Assignments</h2>
                <p className="text-orange-100">No API key needed!</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('paste')}
            className={`flex-1 px-6 py-3 font-medium transition ${
              activeTab === 'paste'
                ? 'border-b-2 border-orange-500 text-orange-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Sparkles className="w-5 h-5 inline mr-2" />
            AI Import
          </button>
          <button
            onClick={() => setActiveTab('help')}
            className={`flex-1 px-6 py-3 font-medium transition ${
              activeTab === 'help'
                ? 'border-b-2 border-orange-500 text-orange-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <FileText className="w-5 h-5 inline mr-2" />
            Instructions
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {activeTab === 'paste' ? (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 mb-2">How it works:</h3>
                <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
                  <li>Go to your Canvas Assignments or Calendar page</li>
                  <li>Select and copy the assignments (Ctrl+A, Ctrl+C)</li>
                  <li>Paste them in the box below</li>
                  <li>Our AI will extract the assignments automatically!</li>
                </ol>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Paste Canvas assignments here:
                </label>
                <textarea
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                  placeholder="Paste your Canvas assignments here...&#10;&#10;Example:&#10;CS 101 - Assignment 1&#10;Due: Nov 20, 2024 at 11:59pm&#10;&#10;MATH 200 - Homework 3&#10;Due: Nov 22, 2024 at 11:59pm"
                  className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none font-mono text-sm"
                />
                <p className="mt-2 text-xs text-gray-500">
                  💡 Tip: The more context you paste, the better the AI can extract assignments
                </p>
              </div>

              <button
                onClick={handlePaste}
                disabled={!pastedText.trim() || pasteMutation.isPending}
                className="w-full px-6 py-3 bg-orange-600 text-white rounded-lg font-medium hover:bg-orange-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {pasteMutation.isPending ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Importing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Import with AI</span>
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="bg-gradient-to-br from-orange-50 to-red-50 border border-orange-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  🎓 Why can't I use the Canvas API?
                </h3>
                <p className="text-gray-700 mb-4">
                  Canvas restricts API access to prevent automated scraping. But don't worry - we have workarounds!
                </p>
              </div>

              <div className="space-y-4">
                <div className="border border-gray-200 rounded-lg p-5">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <span className="bg-orange-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">1</span>
                    AI Copy-Paste (Recommended)
                  </h4>
                  <p className="text-sm text-gray-600 mb-3">Copy assignments from Canvas, paste here, and our AI extracts them.</p>
                  <div className="bg-gray-50 p-3 rounded text-xs font-mono text-gray-700">
                    Canvas → Select All → Copy → Paste in Circa
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg p-5">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">2</span>
                    Canvas Calendar Feed
                  </h4>
                  <p className="text-sm text-gray-600 mb-3">Export Canvas calendar to Google Calendar, then sync with Circa.</p>
                  <ol className="text-xs text-gray-600 space-y-1 list-disc list-inside">
                    <li>In Canvas: Calendar → Calendar Feed → Copy URL</li>
                    <li>In Google Calendar: Add calendar by URL</li>
                    <li>Circa syncs from Google Calendar automatically</li>
                  </ol>
                </div>

                <div className="border border-gray-200 rounded-lg p-5">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                    <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">3</span>
                    Manual Entry
                  </h4>
                  <p className="text-sm text-gray-600">Add assignments one by one using the "New Task" button.</p>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">
                  <strong>Pro Tip:</strong> Methods 1 and 2 are one-time setup. After initial import, 
                  use the calendar feed for automatic updates!
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

