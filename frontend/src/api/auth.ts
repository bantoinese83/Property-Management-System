import client from './client'
import { API_ENDPOINTS } from './endpoints'

interface LoginCredentials {
  username: string
  password: string
}

interface RegisterData extends LoginCredentials {
  email: string
  first_name: string
  last_name: string
  user_type: string
}

interface AuthResponse {
  access: string
  refresh: string
  user: {
    id: number
    username: string
    email: string
    user_type: string
  }
}

export const authAPI = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await client.post<AuthResponse>(API_ENDPOINTS.AUTH.LOGIN, credentials)
    return response.data
  },

  async register(data: RegisterData): Promise<unknown> {
    const response = await client.post(API_ENDPOINTS.AUTH.REGISTER, data)
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await client.post<{ access: string }>(API_ENDPOINTS.AUTH.REFRESH, {
      refresh: refreshToken,
    })
    return response.data
  },

  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
}
