import { useState, useEffect, useCallback, useRef } from 'react'
import { type AxiosError } from 'axios'
import client from '../api/client'

interface UseApiOptions<T = unknown> {
  skip?: boolean
  refetchInterval?: number
  retryOnError?: number
  onSuccess?: (data: T) => void
  onError?: (error: Error) => void
  enableBackgroundRefetch?: boolean
}

interface UseApiResponse<T> {
  data: T | null
  loading: boolean
  error: Error | null
  refetch: () => Promise<void>
  isRefetching: boolean
  isError: boolean
  isSuccess: boolean
  errorMessage?: string
  retry: () => Promise<void>
}

export function useApi<T = unknown>(
  url: string,
  options: UseApiOptions<T> = {}
): UseApiResponse<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(!options.skip)
  const [error, setError] = useState<Error | null>(null)
  const [isRefetching, setIsRefetching] = useState(false)
  const retryCount = useRef(0)

  const fetchData = useCallback(
    async (isRetry = false) => {
      if (options.skip) return

      try {
        if (!isRetry) {
          setIsRefetching(true)
        }
        setError(null)

        const response = await client.get<T>(url)
        setData(response.data)
        retryCount.current = 0

        // Call success callback
        if (options.onSuccess) {
          options.onSuccess(response.data)
        }
      } catch (err) {
        const axiosError = err as AxiosError<{ detail?: string }>
        const error = err instanceof Error ? err : new Error('Unknown error occurred')
        setError(error)

        // Call error callback
        if (options.onError) {
          options.onError(error)
        }

        // Auto-retry logic for server errors
        if (
          options.retryOnError &&
          retryCount.current < options.retryOnError &&
          axiosError.response &&
          typeof axiosError.response.status === 'number' &&
          axiosError.response.status >= 500
        ) {
          retryCount.current++
          setTimeout(() => fetchData(true), 1000 * Math.pow(2, retryCount.current))
        }
      } finally {
        setIsRefetching(false)
        setLoading(false)
      }
    },
    [url, options]
  )

  useEffect(() => {
    if (!options.skip) {
      fetchData()
    }
  }, [url, options.skip, fetchData])

  const retry = useCallback(async () => {
    retryCount.current = 0
    await fetchData()
  }, [fetchData])

  useEffect(() => {
    if (options.refetchInterval) {
      const interval = setInterval(fetchData, options.refetchInterval)
      return () => clearInterval(interval)
    }
  }, [options.refetchInterval, fetchData])

  const isError = !!error
  const isSuccess = !!data && !isError
  const errorMessage = error?.message

  return {
    data,
    loading,
    error,
    refetch: fetchData,
    isRefetching,
    isError,
    isSuccess,
    errorMessage,
    retry,
  }
}
