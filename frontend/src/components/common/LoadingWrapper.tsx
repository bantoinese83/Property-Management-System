import React from 'react'
import { LoadingSpinner } from './LoadingSpinner'

interface LoadingWrapperProps {
  loading: boolean
  children: React.ReactNode
  spinnerSize?: 'sm' | 'md' | 'lg'
  loadingText?: string
  className?: string
  overlay?: boolean
}

export const LoadingWrapper: React.FC<LoadingWrapperProps> = ({
  loading,
  children,
  spinnerSize = 'md',
  loadingText,
  className = '',
  overlay = false,
}) => {
  if (!loading) {
    return <>{children}</>
  }

  if (overlay) {
    return (
      <div className={`relative ${className}`}>
        {children}
        <div className='absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10 rounded-lg'>
          <LoadingSpinner size={spinnerSize} text={loadingText} />
        </div>
      </div>
    )
  }

  return (
    <div className={`flex items-center justify-center p-8 ${className}`}>
      <LoadingSpinner size={spinnerSize} text={loadingText} />
    </div>
  )
}
