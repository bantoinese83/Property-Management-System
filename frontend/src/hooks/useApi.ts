import { useState, useEffect, useCallback, useRef, useMemo } from 'react'
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

  // Memoize options to prevent unnecessary re-renders
  const memoizedOptions = useMemo(
    () => options,
    [options.skip, options.refetchInterval, options.retryOnError]
  )

  const fetchData = useCallback(
    async (isRetry = false) => {
      if (memoizedOptions.skip) return

      try {
        if (!isRetry) {
          setIsRefetching(true)
        }
        setError(null)

        const response = await client.get<T>(url)
        setData(response.data)
        retryCount.current = 0

        // Call success callback
        if (memoizedOptions.onSuccess) {
          memoizedOptions.onSuccess(response.data)
        }
      } catch (err) {
        const axiosError = err as AxiosError<{ detail?: string }>
        const error = err instanceof Error ? err : new Error('Unknown error occurred')
        setError(error)

        // Call error callback
        if (memoizedOptions.onError) {
          memoizedOptions.onError(error)
        }

        // Auto-retry logic for server errors (but not rate limits)
        if (
          memoizedOptions.retryOnError &&
          retryCount.current < memoizedOptions.retryOnError &&
          axiosError.response &&
          typeof axiosError.response.status === 'number' &&
          axiosError.response.status >= 500 &&
          axiosError.response.status !== 429 // Don't retry rate limits
        ) {
          retryCount.current++
          setTimeout(() => fetchData(true), 1000 * Math.pow(2, retryCount.current))
        }
      } finally {
        setIsRefetching(false)
        setLoading(false)
      }
    },
    [url, memoizedOptions]
  )

  useEffect(() => {
    if (!memoizedOptions.skip) {
      fetchData()
    }
  }, [url, memoizedOptions.skip])

  const retry = useCallback(async () => {
    retryCount.current = 0
    await fetchData()
  }, [fetchData])

  useEffect(() => {
    if (memoizedOptions.refetchInterval) {
      const interval = setInterval(fetchData, memoizedOptions.refetchInterval)
      return () => clearInterval(interval)
    }
  }, [memoizedOptions.refetchInterval])

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
