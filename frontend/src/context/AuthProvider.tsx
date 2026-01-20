import React, { useState, useCallback, useEffect } from 'react'
import client from '../api/client'
import type { User, AuthContextType } from './AuthContext.types'
import { AuthContext } from './AuthContext'

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    // Check if user is already authenticated
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          // Verify token works
          const response = await client.get<User>('/users/me/')
          setUser(response.data)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await client.post<{ access: string; refresh: string; user: User }>(
        '/token/',
        { username, password }
      )
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      setUser(response.data.user)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Login failed')
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }, [])

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    loading,
    error,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
