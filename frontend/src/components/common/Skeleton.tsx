import React from 'react'
import { cn } from '../../lib/utils'

interface SkeletonProps {
  className?: string
  variant?: 'default' | 'rounded' | 'circular'
  width?: string | number
  height?: string | number
  lines?: number
  animate?: boolean
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className,
  variant = 'default',
  width,
  height,
  lines = 1,
  animate = true,
}) => {
  const baseClasses = 'bg-gray-200 dark:bg-gray-700'
  const animateClasses = animate ? 'animate-pulse' : ''

  const variantClasses = {
    default: 'rounded',
    rounded: 'rounded-md',
    circular: 'rounded-full',
  }

  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  }

  if (lines > 1) {
    return (
      <div className='space-y-2'>
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={cn(baseClasses, animateClasses, variantClasses[variant], className)}
            style={{
              ...style,
              width: index === lines - 1 ? '60%' : style.width, // Last line shorter
            }}
          />
        ))}
      </div>
    )
  }

  return (
    <div
      className={cn(baseClasses, animateClasses, variantClasses[variant], className)}
      style={style}
    />
  )
}

// Predefined skeleton components for common use cases
export const SkeletonText: React.FC<
  Omit<SkeletonProps, 'variant' | 'height'> & { lines?: number }
> = ({ lines = 3, ...props }) => (
  <Skeleton {...props} lines={lines} height='1rem' className='mb-2' />
)

export const SkeletonAvatar: React.FC<
  Omit<SkeletonProps, 'variant' | 'width' | 'height'>
> = props => <Skeleton {...props} variant='circular' width={40} height={40} />

export const SkeletonButton: React.FC<Omit<SkeletonProps, 'variant' | 'height'>> = props => (
  <Skeleton {...props} variant='rounded' height={40} width={120} />
)

export const SkeletonCard: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn('p-4 border rounded-lg space-y-3', className)}>
    <Skeleton height={20} width='80%' />
    <Skeleton height={16} width='60%' />
    <div className='flex space-x-2'>
      <Skeleton width={80} height={32} variant='rounded' />
      <Skeleton width={80} height={32} variant='rounded' />
    </div>
  </div>
)
