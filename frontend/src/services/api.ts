import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username: email, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (email: string, password: string, full_name?: string) =>
    api.post('/auth/register', { email, password, full_name }),
  getCurrentUser: () => api.get('/auth/me'),
}

// Events API
export const eventsApi = {
  list: (params?: { start_date?: string; end_date?: string }) =>
    api.get('/events/', { params }),
  get: (id: number) => api.get(`/events/${id}`),
  create: (data: any) => api.post('/events/', data),
  update: (id: number, data: any) => api.put(`/events/${id}`, data),
  delete: (id: number) => api.delete(`/events/${id}`),
}

// Tasks API
export const tasksApi = {
  list: (params?: { status?: string }) => api.get('/tasks/', { params }),
  get: (id: number) => api.get(`/tasks/${id}`),
  create: (data: any) => api.post('/tasks/', data),
  update: (id: number, data: any) => api.put(`/tasks/${id}`, data),
  delete: (id: number) => api.delete(`/tasks/${id}`),
}

// Dashboard API
export const dashboardApi = {
  daily: (date?: string) => api.get('/dashboard/daily', { params: { date } }),
  weekly: (start_date?: string) => api.get('/dashboard/weekly', { params: { start_date } }),
  insights: () => api.get('/dashboard/insights'),
}

// Integrations API
export const integrationsApi = {
  list: () => api.get('/integrations/'),
  connectCanvas: (api_key: string, canvas_url: string) =>
    api.post('/integrations/canvas/connect', { api_key, canvas_url }),
  connectNotion: (api_key: string) =>
    api.post('/integrations/notion/connect', { api_key }),
  sync: (id: number) => api.post(`/integrations/${id}/sync`),
  disconnect: (id: number) => api.delete(`/integrations/${id}`),
}

// AI API
export const aiApi = {
  parseEmail: (email_content: string, subject: string) =>
    api.post('/ai/parse-email', { email_content, subject }),
  optimizeSchedule: () => api.post('/ai/optimize-schedule'),
  getOnboardingQuiz: () => api.get('/ai/quiz/onboarding'),
  submitQuiz: (quiz_type: string, answers: any[]) =>
    api.post('/ai/quiz/submit', { quiz_type, answers }),
  analyzeProductivity: () => api.post('/ai/analyze-productivity'),
  scheduleFromPrompt: (prompt: string) =>
    api.post('/ai/schedule-from-prompt', null, { params: { prompt } }),
}

// Google OAuth API
export const googleApi = {
  getLoginUrl: () => api.get('/google/google/login'),
  syncCalendar: () => api.post('/google/google/sync-calendar'),
}

// Manual Import API  
export const manualImportApi = {
  pasteCanvas: (text: string) => api.post('/manual-import/canvas/paste', text, {
    headers: { 'Content-Type': 'text/plain' }
  }),
  manualCanvas: (assignments: any[]) => api.post('/manual-import/canvas/manual', { assignments }),
}

// Users API
export const usersApi = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data: any) => api.put('/users/me', data),
  getPreferences: () => api.get('/users/me/preferences'),
  updatePreferences: (data: any) => api.put('/users/me/preferences', data),
}

