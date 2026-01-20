import * as React from 'react'
import { cn } from '../../lib/utils'
import { Label } from './Label'
import '../../styles/Input.css'
import { Label } from './Label'

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  fullWidth?: boolean
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, fullWidth, ...props }, ref) => {
    const inputId = React.useId()
    const id = props.id || inputId

    return (
      <div className={cn('flex flex-col gap-1.5', fullWidth && 'w-full')}>
        {label && <Label htmlFor={id}>{label}</Label>}
        <input
          id={id}
          type={type}
          className={cn(
            'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-destructive focus-visible:ring-destructive',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <p className='text-xs font-medium text-destructive'>{error}</p>}
      </div>
    )
  }
)
Input.displayName = 'Input'

export { Input }
