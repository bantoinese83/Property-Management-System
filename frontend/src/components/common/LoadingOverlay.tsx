import React from 'react'
import { cn } from '../../lib/utils'
import { LoadingSpinner } from './LoadingSpinner'

interface LoadingOverlayProps {
  isLoading: boolean
  children: React.ReactNode
  message?: string
  variant?: 'spinner' | 'pulse' | 'dots' | 'bars'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  blur?: boolean
  className?: string
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  children,
  message = 'Loading...',
  variant = 'spinner',
  size = 'md',
  blur = false,
  className,
}) => {
  if (!isLoading) {
    return <>{children}</>
  }

  return (
    <div className={cn('relative', className)}>
      {/* Original content */}
      <div className={cn('transition-all duration-200', blur && 'blur-sm opacity-50')}>
        {children}
      </div>

      {/* Loading overlay */}
      <div className='absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-inherit'>
        <div className='bg-white dark:bg-gray-800 rounded-lg shadow-lg border p-6 min-w-[200px]'>
          <LoadingSpinner
            variant={variant}
            size={size}
            message={message}
            showMessage
            className='flex-col'
          />
        </div>
      </div>
    </div>
  )
}
