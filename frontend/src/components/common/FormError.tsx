import React from 'react'
import { AlertCircle, Info } from 'lucide-react'
import { cn } from '../../lib/utils'

interface FormErrorProps {
  error?: string | string[]
  className?: string
  showIcon?: boolean
  variant?: 'error' | 'warning' | 'info'
}

export const FormError: React.FC<FormErrorProps> = ({
  error,
  className,
  showIcon = true,
  variant = 'error',
}) => {
  if (!error) return null

  const errorMessage = Array.isArray(error) ? error[0] : error

  if (!errorMessage) return null

  const getIcon = () => {
    if (!showIcon) return null

    switch (variant) {
      case 'error':
        return <AlertCircle className='w-4 h-4 text-red-600 flex-shrink-0' />
      case 'warning':
        return <AlertCircle className='w-4 h-4 text-yellow-600 flex-shrink-0' />
      case 'info':
        return <Info className='w-4 h-4 text-blue-600 flex-shrink-0' />
      default:
        return <AlertCircle className='w-4 h-4 text-red-600 flex-shrink-0' />
    }
  }

  const getStyles = () => {
    const baseStyles = 'flex items-start gap-2 text-sm px-3 py-2 rounded-md'

    switch (variant) {
      case 'error':
        return cn(baseStyles, 'bg-red-50 text-red-700 border border-red-200')
      case 'warning':
        return cn(baseStyles, 'bg-yellow-50 text-yellow-700 border border-yellow-200')
      case 'info':
        return cn(baseStyles, 'bg-blue-50 text-blue-700 border border-blue-200')
      default:
        return cn(baseStyles, 'bg-red-50 text-red-700 border border-red-200')
    }
  }

  return (
    <div className={cn(getStyles(), className)}>
      {getIcon()}
      <span className='leading-5'>{errorMessage}</span>
    </div>
  )
}
