import React from 'react'
import { AlertCircle } from 'lucide-react'
import { cn } from '../../lib/utils'

interface ErrorMessageProps {
  message: string
  className?: string
  title?: string
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  className,
  title = 'Error',
}) => {
  return (
    <div className={cn('flex flex-col items-center justify-center p-6 text-center', className)}>
      <div className='flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10 text-destructive mb-4'>
        <AlertCircle className='h-6 w-6' />
      </div>
      <h3 className='text-lg font-semibold text-foreground mb-2'>{title}</h3>
      <p className='text-sm text-muted-foreground max-w-md'>{message}</p>
    </div>
  )
}
