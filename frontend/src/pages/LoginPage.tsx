import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Input } from '../components/common/Input'
import { Button } from '../components/common/Button'

const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className='login-page'>
      <div className='login-container'>
        <div className='login-header'>
          <h1>Property Management</h1>
          <p>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className='login-form'>
          {error && <div className='alert alert-error'>{error}</div>}

          <Input
            label='Username'
            type='text'
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder='Enter your username'
            autoComplete='username'
            fullWidth
            required
          />

          <Input
            label='Password'
            type='password'
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder='Enter your password'
            autoComplete='current-password'
            fullWidth
            required
          />

          <Button type='submit' variant='primary' fullWidth loading={loading}>
            Sign In
          </Button>
        </form>

        <div className='login-footer'>
          <p>Demo credentials: admin / admin123</p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
