import React from 'react'
import { RefreshCw } from 'lucide-react'
import { Button } from './Button'

interface RetryButtonProps {
  onRetry: () => void
  loading?: boolean
  text?: string
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'sm' | 'default' | 'lg'
  className?: string
}

export const RetryButton: React.FC<RetryButtonProps> = ({
  onRetry,
  loading = false,
  text = 'Try Again',
  variant = 'outline',
  size = 'sm',
  className
}) => {
  return (
    <Button
      onClick={onRetry}
      disabled={loading}
      variant={variant}
      size={size}
      className={className}
    >
      {loading ? (
        <>
          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
          Retrying...
        </>
      ) : (
        <>
          <RefreshCw className="w-4 h-4 mr-2" />
          {text}
        </>
      )}
    </Button>
  )
}