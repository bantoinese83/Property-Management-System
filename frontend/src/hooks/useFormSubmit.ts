import { useState, useCallback } from 'react'
import { AxiosError } from 'axios'
import { useToast } from '../components/common/ToastContainer'
import { getUserFriendlyError } from '../utils/errorMessages'

interface UseFormSubmitOptions {
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
  successMessage?: string
  showSuccessToast?: boolean
  showErrorToast?: boolean
}

interface UseFormSubmitReturn {
  submit: (submitFn: () => Promise<any>) => Promise<any>
  loading: boolean
  error: string | null
  clearError: () => void
  retry: () => Promise<any>
}

export function useFormSubmit(options: UseFormSubmitOptions = {}): UseFormSubmitReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastSubmitFn, setLastSubmitFn] = useState<(() => Promise<any>) | null>(null)

  const { showSuccess, showError } = useToast()
  const {
    onSuccess,
    onError,
    successMessage,
    showSuccessToast = true,
    showErrorToast = true
  } = options

  const submit = useCallback(async (submitFn: () => Promise<any>) => {
    setLoading(true)
    setError(null)
    setLastSubmitFn(() => submitFn)

    try {
      const result = await submitFn()

      if (showSuccessToast && successMessage) {
        showSuccess('Success', successMessage)
      }

      if (onSuccess) {
        onSuccess(result)
      }

      return result
    } catch (err) {
      const axiosError = err as AxiosError
      const userFriendlyError = getUserFriendlyError(axiosError)

      setError(userFriendlyError)

      if (showErrorToast) {
        showError('Error', userFriendlyError)
      }

      if (onError) {
        onError(err as Error)
      }

      throw err
    } finally {
      setLoading(false)
    }
  }, [showSuccess, showError, onSuccess, onError, successMessage, showSuccessToast, showErrorToast])

  const retry = useCallback(async () => {
    if (lastSubmitFn) {
      return submit(lastSubmitFn)
    }
  }, [submit, lastSubmitFn])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    submit,
    loading,
    error,
    clearError,
    retry
  }
}