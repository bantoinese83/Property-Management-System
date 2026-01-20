import React, { useEffect, useState } from 'react'
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react'
import { cn } from '../../lib/utils'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastProps {
  id: string
  type: ToastType
  title: string
  message?: string
  duration?: number
  onClose: (id: string) => void
  action?: {
    label: string
    onClick: () => void
  }
}

export const Toast: React.FC<ToastProps> = ({
  id,
  type,
  title,
  message,
  duration = 5000,
  onClose,
  action,
}) => {
  const [isVisible, setIsVisible] = useState(true)
  const [isLeaving, setIsLeaving] = useState(false)

  const handleClose = useCallback(() => {
    setIsLeaving(true)
    setTimeout(() => {
      setIsVisible(false)
      onClose(id)
    }, 300) // Match animation duration
  }, [onClose, id])

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose()
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [duration, handleClose])

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className='w-5 h-5 text-green-600' />
      case 'error':
        return <AlertCircle className='w-5 h-5 text-red-600' />
      case 'warning':
        return <AlertTriangle className='w-5 h-5 text-yellow-600' />
      case 'info':
        return <Info className='w-5 h-5 text-blue-600' />
      default:
        return <Info className='w-5 h-5 text-blue-600' />
    }
  }

  const getStyles = () => {
    const baseStyles =
      'flex items-start gap-3 p-4 rounded-lg border shadow-lg transition-all duration-300'

    switch (type) {
      case 'success':
        return cn(baseStyles, 'bg-green-50 border-green-200 text-green-900')
      case 'error':
        return cn(baseStyles, 'bg-red-50 border-red-200 text-red-900')
      case 'warning':
        return cn(baseStyles, 'bg-yellow-50 border-yellow-200 text-yellow-900')
      case 'info':
        return cn(baseStyles, 'bg-blue-50 border-blue-200 text-blue-900')
      default:
        return cn(baseStyles, 'bg-gray-50 border-gray-200 text-gray-900')
    }
  }

  if (!isVisible) return null

  return (
    <div
      className={cn(
        getStyles(),
        'max-w-md w-full',
        isLeaving && 'opacity-0 transform translate-x-full'
      )}
    >
      <div className='flex-shrink-0 mt-0.5'>{getIcon()}</div>

      <div className='flex-1 min-w-0'>
        <div className='flex items-start justify-between'>
          <div className='flex-1'>
            <h4 className='text-sm font-semibold leading-5'>{title}</h4>
            {message && <p className='text-sm leading-5 mt-1 opacity-90'>{message}</p>}
            {action && (
              <button
                onClick={action.onClick}
                className='text-sm font-medium underline hover:no-underline mt-2 inline-block'
              >
                {action.label}
              </button>
            )}
          </div>

          <button
            onClick={handleClose}
            className='flex-shrink-0 ml-3 p-1 rounded-md hover:bg-black/10 transition-colors'
          >
            <X className='w-4 h-4' />
          </button>
        </div>
      </div>
    </div>
  )
}
