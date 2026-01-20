import { Component, type ErrorInfo, type ReactNode } from 'react'
import { Button } from './Button'
import { AlertCircle, RefreshCw, Home } from 'lucide-react'

interface Props {
  children?: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
  showErrorDetails?: boolean
  maxRetries?: number
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  retryCount: number
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    retryCount: 0,
  }

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
      retryCount: 0,
    }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo)

    this.setState({ errorInfo })

    // Call optional error callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // Optional error reporting (could integrate with services like Sentry)
    if (import.meta.env.PROD) {
      // Report to error tracking service
      this.reportError(error, errorInfo)
    }
  }

  private reportError = (error: Error, errorInfo: ErrorInfo) => {
    // Placeholder for error reporting service integration
    console.error('Error reported:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    })
  }

  private handleRetry = () => {
    const { maxRetries = 3 } = this.props
    const { retryCount } = this.state

    if (retryCount < maxRetries) {
      this.setState(prevState => ({
        hasError: false,
        error: null,
        errorInfo: null,
        retryCount: prevState.retryCount + 1,
      }))
    }
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
    })
    window.location.assign('/')
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      const { error, errorInfo, retryCount } = this.state
      const { maxRetries = 3, showErrorDetails = false } = this.props
      const canRetry = retryCount < maxRetries

      return (
        <div className='flex min-h-screen flex-col items-center justify-center p-6 text-center bg-gray-50'>
          <div className='max-w-md w-full bg-white rounded-lg shadow-lg p-8 border border-gray-200'>
            <div className='flex items-center justify-center w-16 h-16 mx-auto mb-6 bg-red-100 rounded-full'>
              <AlertCircle className='w-8 h-8 text-red-600' />
            </div>

            <h1 className='mb-4 text-2xl font-bold text-gray-900'>Oops! Something went wrong</h1>

            <p className='mb-6 text-gray-600 leading-relaxed'>
              We're sorry, but we encountered an unexpected issue. Our team has been notified and is
              working to fix it.
            </p>

            <p className='mb-6 text-sm text-gray-500'>
              In the meantime, try refreshing the page or contact support if the problem persists.
            </p>

            {retryCount > 0 && (
              <p className='mb-4 text-sm text-gray-500'>
                Retry attempt: {retryCount} of {maxRetries}
              </p>
            )}

            {showErrorDetails && errorInfo && (
              <details className='mb-6 text-left'>
                <summary className='cursor-pointer text-sm text-gray-500 hover:text-gray-700 mb-2'>
                  Technical Details
                </summary>
                <div className='bg-gray-100 p-3 rounded text-xs font-mono text-gray-800 overflow-auto max-h-32'>
                  <div className='mb-2'>
                    <strong>Error:</strong> {error?.name}: {error?.message}
                  </div>
                  {error?.stack && (
                    <div className='mb-2'>
                      <strong>Stack:</strong>
                      <pre className='whitespace-pre-wrap mt-1'>{error.stack}</pre>
                    </div>
                  )}
                  <div>
                    <strong>Component Stack:</strong>
                    <pre className='whitespace-pre-wrap mt-1'>{errorInfo.componentStack}</pre>
                  </div>
                </div>
              </details>
            )}

            <div className='flex flex-col sm:flex-row gap-3 justify-center'>
              {canRetry && (
                <Button
                  onClick={this.handleRetry}
                  variant='outline'
                  className='flex items-center gap-2'
                >
                  <RefreshCw className='w-4 h-4' />
                  Try Again
                </Button>
              )}

              <Button onClick={this.handleReset} className='flex items-center gap-2'>
                <Home className='w-4 h-4' />
                Go Home
              </Button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
