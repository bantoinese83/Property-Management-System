import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider, useAuth } from './AuthContext'

// Mock the API client
vi.mock('../api/client', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

import client from '../api/client'

// Test component that uses the auth context
function TestComponent() {
  const { user, login, logout, loading } = useAuth()

  const handleLogin = () => {
    login('testuser', 'testpass')
  }

  const handleLogout = () => {
    logout()
  }

  if (loading) return <div>Loading...</div>

  return (
    <div>
      <div data-testid="user-info">
        {user ? `Logged in as: ${user.username}` : 'Not logged in'}
      </div>
      <button onClick={handleLogin}>Login</button>
      <button onClick={handleLogout}>Logout</button>
    </div>
  )
}

describe('AuthContext', () => {
  const mockClient = vi.mocked(client)

  beforeEach(() => {
    vi.clearAllMocks()
    // Clear localStorage
    localStorage.clear()
  })

  it('provides auth context to children', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    expect(screen.getByText('Not logged in')).toBeInTheDocument()
  })

  it('handles successful login', async () => {
    const user = userEvent.setup()
    const mockResponse = {
      data: {
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: {
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
          user_type: 'owner',
        },
      },
    }

    mockClient.post.mockResolvedValueOnce(mockResponse)

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    const loginButton = screen.getByRole('button', { name: /login/i })
    await user.click(loginButton)

    await waitFor(() => {
      expect(screen.getByText('Logged in as: testuser')).toBeInTheDocument()
    })

    expect(localStorage.getItem('access_token')).toBe('mock-access-token')
    expect(localStorage.getItem('refresh_token')).toBe('mock-refresh-token')
  })

  it('handles login error', async () => {
    const user = userEvent.setup()
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    mockClient.post.mockRejectedValueOnce(new Error('Invalid credentials'))

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    const loginButton = screen.getByRole('button', { name: /login/i })
    await user.click(loginButton)

    // Should still show "Not logged in" since login failed
    expect(screen.getByText('Not logged in')).toBeInTheDocument()

    consoleSpy.mockRestore()
  })

  it('handles logout', async () => {
    const user = userEvent.setup()

    // First login
    const mockResponse = {
      data: {
        access: 'mock-access-token',
        refresh: 'mock-refresh-token',
        user: { id: 1, username: 'testuser', email: 'test@example.com', user_type: 'owner' },
      },
    }
    mockClient.post.mockResolvedValueOnce(mockResponse)

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    // Login first
    const loginButton = screen.getByRole('button', { name: /login/i })
    await user.click(loginButton)

    await waitFor(() => {
      expect(screen.getByText('Logged in as: testuser')).toBeInTheDocument()
    })

    // Now logout
    const logoutButton = screen.getByRole('button', { name: /logout/i })
    await user.click(logoutButton)

    await waitFor(() => {
      expect(screen.getByText('Not logged in')).toBeInTheDocument()
    })

    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })

  it('throws error when useAuth is used outside provider', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    expect(() => {
      render(<TestComponent />)
    }).toThrow('useAuth must be used within AuthProvider')

    consoleSpy.mockRestore()
  })
})