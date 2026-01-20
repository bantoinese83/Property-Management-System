export interface User {
  id: number
  username: string
  email: string
  user_type: 'admin' | 'manager' | 'owner' | 'tenant'
}

export interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
  error: Error | null
}
