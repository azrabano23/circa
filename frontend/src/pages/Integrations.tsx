import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { integrationsApi } from '../services/api'
import { Calendar, Mail, BookOpen, FileText, Activity, CheckCircle, XCircle } from 'lucide-react'
import CanvasManualImport from '../components/CanvasManualImport'

export default function Integrations() {
  const [canvasKey, setCanvasKey] = useState('')
  const [canvasUrl, setCanvasUrl] = useState('https://canvas.instructure.com')
  const [notionKey, setNotionKey] = useState('')
  const [showCanvasImport, setShowCanvasImport] = useState(false)
  
  const queryClient = useQueryClient()

  const { data: integrations } = useQuery({
    queryKey: ['integrations'],
    queryFn: () => integrationsApi.list().then((res) => res.data),
  })

  const connectCanvasMutation = useMutation({
    mutationFn: () => integrationsApi.connectCanvas(canvasKey, canvasUrl),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
      setCanvasKey('')
    },
  })

  const connectNotionMutation = useMutation({
    mutationFn: () => integrationsApi.connectNotion(notionKey),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
      setNotionKey('')
    },
  })

  const syncMutation = useMutation({
    mutationFn: (id: number) => integrationsApi.sync(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] })
    },
  })

  const availableIntegrations = [
    {
      name: 'Google Calendar',
      description: 'Sync events and schedules from Google Calendar',
      icon: Calendar,
      provider: 'google',
      color: 'blue',
    },
    {
      name: 'Gmail',
      description: 'Parse emails for deadlines and tasks',
      icon: Mail,
      provider: 'gmail',
      color: 'red',
    },
    {
      name: 'Canvas LMS',
      description: 'Import assignments and deadlines from Canvas',
      icon: BookOpen,
      provider: 'canvas',
      color: 'orange',
    },
    {
      name: 'Notion',
      description: 'Sync tasks and databases from Notion',
      icon: FileText,
      provider: 'notion',
      color: 'gray',
    },
    {
      name: 'Health Data',
      description: 'Track sleep, exercise, and wellness metrics',
      icon: Activity,
      provider: 'health',
      color: 'green',
    },
  ]

  const getIntegrationStatus = (provider: string) => {
    return integrations?.find((i: any) => i.provider === provider)
  }

  return (
    <div className="space-y-6">
      {showCanvasImport && <CanvasManualImport onClose={() => setShowCanvasImport(false)} />}
      
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Integrations</h1>
        <p className="text-gray-600 mt-1">
          Connect your accounts to optimize your schedule
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {availableIntegrations.map((integration) => {
          const Icon = integration.icon
          const status = getIntegrationStatus(integration.provider)
          const isConnected = status?.is_active

          return (
            <div
              key={integration.provider}
              className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <div className={`p-3 bg-${integration.color}-100 rounded-lg`}>
                    <Icon className={`w-6 h-6 text-${integration.color}-600`} />
                  </div>
                  <div className="ml-4">
                    <h3 className="font-semibold text-gray-900">{integration.name}</h3>
                    <p className="text-sm text-gray-600">{integration.description}</p>
                  </div>
                </div>
                {isConnected ? (
                  <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                ) : (
                  <XCircle className="w-6 h-6 text-gray-300 flex-shrink-0" />
                )}
              </div>

              {integration.provider === 'canvas' && !isConnected && (
                <div className="mt-4 space-y-3">
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-3">
                    <p className="text-sm text-orange-800 mb-2">
                      <strong>Canvas API not available?</strong> No problem!
                    </p>
                    <p className="text-xs text-orange-700">
                      Use our AI-powered import tool to copy/paste assignments from Canvas.
                    </p>
                  </div>
                  
                  <button
                    onClick={() => setShowCanvasImport(true)}
                    className="w-full px-4 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:from-orange-600 hover:to-red-600 transition font-medium"
                  >
                    📋 Import Canvas Assignments (No API Key Needed)
                  </button>
                  
                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <div className="w-full border-t border-gray-300"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                      <span className="px-2 bg-white text-gray-500">or use API key</span>
                    </div>
                  </div>
                  
                  <input
                    type="url"
                    placeholder="Canvas URL"
                    value={canvasUrl}
                    onChange={(e) => setCanvasUrl(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                  <input
                    type="password"
                    placeholder="Canvas API Key (if you have one)"
                    value={canvasKey}
                    onChange={(e) => setCanvasKey(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                  <button
                    onClick={() => connectCanvasMutation.mutate()}
                    disabled={!canvasKey || connectCanvasMutation.isPending}
                    className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
                  >
                    Connect with API Key
                  </button>
                </div>
              )}

              {integration.provider === 'notion' && !isConnected && (
                <div className="mt-4 space-y-3">
                  <input
                    type="password"
                    placeholder="Notion Integration Key"
                    value={notionKey}
                    onChange={(e) => setNotionKey(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                  <button
                    onClick={() => connectNotionMutation.mutate()}
                    disabled={!notionKey || connectNotionMutation.isPending}
                    className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
                  >
                    Connect Notion
                  </button>
                </div>
              )}

              {(integration.provider === 'google' || integration.provider === 'gmail') && !isConnected && (
                <button 
                  onClick={async () => {
                    try {
                      const response = await fetch('http://localhost:8000/api/v1/google/google/login')
                      const data = await response.json()
                      if (data.authorization_url) {
                        window.open(data.authorization_url, '_blank', 'width=600,height=700')
                      }
                    } catch (error) {
                      console.error('Error connecting Google:', error)
                      alert('Error: Make sure backend is running')
                    }
                  }}
                  className="mt-4 w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                >
                  🔗 Connect with Google (Calendar + Gmail)
                </button>
              )}

              {integration.provider === 'health' && !isConnected && (
                <button className="mt-4 w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition">
                  Connect Health Data
                </button>
              )}

              {isConnected && (
                <div className="mt-4 flex space-x-2">
                  <button
                    onClick={() => syncMutation.mutate(status.id)}
                    disabled={syncMutation.isPending}
                    className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
                  >
                    Sync Now
                  </button>
                  <button className="flex-1 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition">
                    Disconnect
                  </button>
                </div>
              )}

              {status?.last_sync_at && (
                <p className="mt-3 text-xs text-gray-500">
                  Last synced: {new Date(status.last_sync_at).toLocaleString()}
                </p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

