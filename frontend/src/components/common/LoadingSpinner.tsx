import React from 'react'
import { cn } from '../../lib/utils'
import { Loader2 } from 'lucide-react'

interface LoadingSpinnerProps {
  className?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'spinner' | 'pulse' | 'dots' | 'bars'
  color?: 'primary' | 'secondary' | 'muted'
  message?: string
  showMessage?: boolean
  'aria-label'?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  className,
  size = 'md',
  variant = 'spinner',
  color = 'primary',
  message = 'Loading...',
  showMessage = false,
  'aria-label': ariaLabel,
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
  }

  const colorClasses = {
    primary: 'text-primary',
    secondary: 'text-secondary',
    muted: 'text-muted-foreground',
  }

  const renderSpinner = () => {
    switch (variant) {
      case 'pulse':
        return (
          <div
            className={cn('animate-pulse rounded-full bg-current opacity-75', sizeClasses[size])}
          />
        )

      case 'dots':
        return (
          <div className='flex space-x-1'>
            {[0, 1, 2].map(i => (
              <div
                key={i}
                className={cn(
                  'animate-bounce rounded-full bg-current',
                  size === 'sm' ? 'h-2 w-2' : size === 'md' ? 'h-3 w-3' : 'h-4 w-4'
                )}
                style={{ animationDelay: `${i * 0.1}s` }}
              />
            ))}
          </div>
        )

      case 'bars':
        return (
          <div className='flex space-x-1'>
            {[0, 1, 2, 3].map(i => (
              <div
                key={i}
                className={cn(
                  'animate-pulse bg-current',
                  size === 'sm' ? 'h-3 w-1' : size === 'md' ? 'h-4 w-1.5' : 'h-5 w-2'
                )}
                style={{ animationDelay: `${i * 0.1}s` }}
              />
            ))}
          </div>
        )

      default: // spinner
        return <Loader2 className={cn('animate-spin', sizeClasses[size], colorClasses[color])} />
    }
  }

  return (
    <div
      className={cn('flex flex-col items-center justify-center gap-3', className)}
      role='status'
      aria-label={ariaLabel || message}
    >
      {renderSpinner()}

      {showMessage && <p className={cn('text-sm font-medium', colorClasses[color])}>{message}</p>}

      <span className='sr-only'>{message}</span>
    </div>
  )
}
