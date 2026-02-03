import { create } from 'zustand'
import { api } from '@/lib/api'
import { User } from '@/types'

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (userData: {
    email: string
    password: string
    full_name: string
    phone?: string
  }) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: true,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      const data = await api.login(email, password)
      const user = await api.getCurrentUser()
      set({ user, token: data.access_token, isLoading: false })
    } catch (err: any) {
      const message =
        err.response?.data?.detail || 'Invalid email or password'
      set({ error: message, isLoading: false })
      throw err
    }
  },

  register: async (userData) => {
    set({ isLoading: true, error: null })
    try {
      await api.register(userData)
      set({ isLoading: false })
    } catch (err: any) {
      const message =
        err.response?.data?.detail || 'Registration failed. Please try again.'
      set({ error: message, isLoading: false })
      throw err
    }
  },

  logout: () => {
    api.removeToken()
    set({ user: null, token: null, isLoading: false, error: null })
  },

  checkAuth: async () => {
    const token = api.getToken()
    if (!token) {
      set({ user: null, token: null, isLoading: false })
      return
    }
    try {
      const user = await api.getCurrentUser()
      set({ user, token, isLoading: false })
    } catch {
      api.removeToken()
      set({ user: null, token: null, isLoading: false })
    }
  },

  clearError: () => set({ error: null }),
}))
