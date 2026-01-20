import axios, { type AxiosInstance, AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { getUserFriendlyError } from '../utils/errorMessages'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

interface TokenResponse {
  access: string
  refresh: string
}

declare module 'axios' {
  interface AxiosError {
    userFriendlyMessage?: string
    originalError?: AxiosError
  }
}

class APIClient {
  private client: AxiosInstance
  private refreshTokenPromise: Promise<string> | null = null

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      config => {
        const token = localStorage.getItem('access_token')
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      error => Promise.reject(error)
    )

    // Response interceptor
    this.client.interceptors.response.use(
      response => response,
      async (error: AxiosError) => {
        const originalRequest = error.config

        // Handle token refresh for 401 errors
        if (error.response?.status === 401 && originalRequest && !this.isRetry(originalRequest)) {
          if (!this.refreshTokenPromise) {
            this.refreshTokenPromise = this.performTokenRefresh()
          }

          try {
            const newToken = await this.refreshTokenPromise
            this.refreshTokenPromise = null

            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`
            }
            return this.client(originalRequest)
          } catch {
            this.logout()
            window.location.href = '/login'
            return Promise.reject(error)
          }
        }

        // Transform error messages to be user-friendly
        if (error.response?.data) {
          const transformedError = this.transformError(error)
          return Promise.reject(transformedError)
        }

        return Promise.reject(error)
      }
    )
  }

  private async performTokenRefresh(): Promise<string> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    try {
      const { data } = await axios.post<TokenResponse>(`${API_BASE_URL}/token/refresh/`, {
        refresh: refreshToken,
      })
      localStorage.setItem('access_token', data.access)
      return data.access
    } catch (error) {
      this.logout()
      throw error
    }
  }

  private isRetry(config: InternalAxiosRequestConfig): boolean {
    const retryCount = config.headers?.['X-Retry-Count']
    return retryCount ? parseInt(String(retryCount)) > 0 : false
  }

  private logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  private transformError(error: AxiosError): AxiosError {
    // Create a new error with user-friendly message
    const userFriendlyMessage = getUserFriendlyError(error)

    const transformedError = new AxiosError(
      userFriendlyMessage,
      error.code,
      error.config,
      error.request,
      error.response
    )

    // Preserve original error details for debugging
    transformedError.userFriendlyMessage = userFriendlyMessage
    transformedError.originalError = error

    return transformedError
  }

  public getClient(): AxiosInstance {
    return this.client
  }

  public async login(username: string, password: string) {
    const response = await this.client.post<TokenResponse>('/token/', {
      username,
      password,
    })
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    return response.data
  }

  public logout_user() {
    this.logout()
  }
}

const apiClient = new APIClient(API_BASE_URL)
export default apiClient.getClient()
