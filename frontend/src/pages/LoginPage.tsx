import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Building2, Eye, EyeOff } from 'lucide-react'

const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Login form submitted with:', { username, password })
    setError('')
    setLoading(true)

    try {
      console.log('Attempting login...')
      await login(username, password)
      console.log('Login successful, navigating to dashboard...')
      navigate('/dashboard')
    } catch (err) {
      console.error('Login failed:', err)
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="flex justify-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary">
              <Building2 className="h-8 w-8 text-primary-foreground" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
            Welcome back
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Sign in to your Property Management account
          </p>
        </div>

        {/* Login Form */}
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Sign in</CardTitle>
            <CardDescription className="text-center">
              Enter your credentials to access your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-md bg-red-50 dark:bg-red-900/50 p-4">
                  <div className="flex">
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                        Authentication Error
                      </h3>
                      <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                        <p>{error}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  className="w-full"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full pr-10"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400 hover:text-gray-500" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400 hover:text-gray-500" />
                    )}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={loading}
              >
                {loading ? "Signing in..." : "Sign in"}
              </Button>
            </form>

            {/* Demo Credentials */}
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <div className="text-center">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Demo Credentials
                </p>
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-500 bg-gray-50 dark:bg-gray-800 rounded-md p-3 font-mono">
                  <div>Username: admin</div>
                  <div>Password: admin123</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default LoginPage
