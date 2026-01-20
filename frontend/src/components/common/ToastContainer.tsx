import React, { createContext, useContext, useState, useCallback } from 'react'
import { Toast, type ToastProps, type ToastType } from './Toast'

interface ToastContextType {
  showToast: (type: ToastType, title: string, message?: string, options?: {
    duration?: number
    action?: { label: string; onClick: () => void }
  }) => void
  showError: (title: string, message?: string) => void
  showSuccess: (title: string, message?: string) => void
  showWarning: (title: string, message?: string) => void
  showInfo: (title: string, message?: string) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

interface ToastItem extends Omit<ToastProps, 'onClose'> {}

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const showToast = useCallback((
    type: ToastType,
    title: string,
    message?: string,
    options?: {
      duration?: number
      action?: { label: string; onClick: () => void }
    }
  ) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
    const toast: ToastItem = {
      id,
      type,
      title,
      message,
      duration: options?.duration ?? 5000,
      action: options?.action
    }

    setToasts(prev => [...prev, toast])
  }, [])

  const showError = useCallback((title: string, message?: string) => {
    showToast('error', title, message)
  }, [showToast])

  const showSuccess = useCallback((title: string, message?: string) => {
    showToast('success', title, message)
  }, [showToast])

  const showWarning = useCallback((title: string, message?: string) => {
    showToast('warning', title, message)
  }, [showToast])

  const showInfo = useCallback((title: string, message?: string) => {
    showToast('info', title, message)
  }, [showToast])

  const value: ToastContextType = {
    showToast,
    showError,
    showSuccess,
    showWarning,
    showInfo
  }

  return (
    <ToastContext.Provider value={value}>
      {children}

      {/* Toast Container */}
      <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            {...toast}
            onClose={removeToast}
          />
        ))}
      </div>
    </ToastContext.Provider>
  )
}