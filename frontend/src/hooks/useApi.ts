import { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import { type AxiosError } from 'axios'
import client from '../api/client'
import { useToast } from '../components/common/ToastContainer'
import { isRetryableError } from '../utils/errorMessages'

interface UseApiOptions<T = unknown> {
  skip?: boolean
  refetchInterval?: number
  retryOnError?: number
  onSuccess?: (data: T) => void
  onError?: (error: Error) => void
  enableBackgroundRefetch?: boolean
  showErrorToast?: boolean
  errorMessage?: string
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
  const { showError } = useToast()

  // Memoize options to prevent unnecessary re-renders
  const memoizedOptions = useMemo(
    () => options,
    [options.skip, options.refetchInterval, options.retryOnError] // eslint-disable-line react-hooks/exhaustive-deps
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

        // Show error toast if enabled (default: true for most cases)
        const showToast = options.showErrorToast !== false
        if (showToast && !isRetry) {
          const errorMessage = options.errorMessage || error.message || 'Something went wrong'
          showError('Error', errorMessage)
        }

        // Call error callback
        if (memoizedOptions.onError) {
          memoizedOptions.onError(error)
        }

        // Auto-retry logic for retryable errors
        if (
          memoizedOptions.retryOnError &&
          retryCount.current < memoizedOptions.retryOnError &&
          isRetryableError(axiosError)
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
  }, [url, memoizedOptions.skip, fetchData])

  const retry = useCallback(async () => {
    retryCount.current = 0
    await fetchData()
  }, [fetchData])

  useEffect(() => {
    if (memoizedOptions.refetchInterval) {
      const interval = setInterval(fetchData, memoizedOptions.refetchInterval)
      return () => clearInterval(interval)
    }
  }, [memoizedOptions.refetchInterval, fetchData])

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
