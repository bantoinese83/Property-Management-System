import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useApi } from './useApi'

// Mock axios
vi.mock('../api/client', () => ({
  default: {
    get: vi.fn(),
  },
}))

import client from '../api/client'

describe('useApi', () => {
  const mockClient = vi.mocked(client)

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns initial state', () => {
    const { result } = renderHook(() => useApi('/api/test'))

    expect(result.current.data).toBeNull()
    expect(result.current.loading).toBe(true)
    expect(result.current.error).toBeNull()
  })

  it('fetches data successfully', async () => {
    const mockData = { id: 1, name: 'Test' }
    mockClient.get.mockResolvedValueOnce({ data: mockData })

    const { result } = renderHook(() => useApi('/api/test'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toEqual(mockData)
    expect(result.current.error).toBeNull()
    expect(mockClient.get).toHaveBeenCalledWith('/api/test')
  })

  it('handles fetch error', async () => {
    const mockError = new Error('Network error')
    mockClient.get.mockRejectedValueOnce(mockError)

    const { result } = renderHook(() => useApi('/api/test'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.data).toBeNull()
    expect(result.current.error).toEqual(mockError)
  })

  it('skips fetch when skip is true', () => {
    const { result } = renderHook(() => useApi('/api/test', { skip: true }))

    expect(result.current.loading).toBe(false)
    expect(mockClient.get).not.toHaveBeenCalled()
  })

  it('retries on error when retryOnError is set', async () => {
    const mockErrorResponse = {
      response: { status: 500 },
    }
    mockClient.get.mockRejectedValueOnce(mockErrorResponse)

    const { result } = renderHook(() => useApi('/api/test', { retryOnError: 2 }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Should retry once (initial + 1 retry)
    expect(mockClient.get).toHaveBeenCalledTimes(2)
  })

  it('refetches data when refetch is called', async () => {
    const mockData = { id: 1, name: 'Test' }
    mockClient.get.mockResolvedValue({ data: mockData })

    const { result } = renderHook(() => useApi('/api/test'))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Call refetch
    await result.current.refetch()

    expect(mockClient.get).toHaveBeenCalledTimes(2)
  })
})
