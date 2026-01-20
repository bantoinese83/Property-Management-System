import React from 'react'
import { cn } from '../../lib/utils'
import { LoadingSpinner } from './LoadingSpinner'

interface LoadingOverlayProps {
  isLoading: boolean
  children: React.ReactNode
  message?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  blur?: boolean
  className?: string
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  children,
  message = 'Loading...',
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
            size={size === 'xl' ? 'lg' : size}
            className='flex-col'
            text={message}
          />
        </div>
      </div>
    </div>
  )
}
