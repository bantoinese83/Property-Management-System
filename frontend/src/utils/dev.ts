/**
 * Development utilities for debugging and performance monitoring
 * Only available in development mode
 */

// Define AxiosResponse type locally to avoid import issues
interface AxiosResponse<T = any> {
  data: T
  status: number
  statusText: string
  headers: any
  config: any
  request?: any
}

// Development-only utilities
export const devUtils = {
  // Log API requests in development
  logApiCall: (method: string, url: string, data?: any, response?: AxiosResponse) => {
    if (import.meta.env.DEV) {
      console.group(`🚀 API ${method.toUpperCase()}: ${url}`)
      if (data) console.log('Request:', data)
      if (response) {
        console.log('Response:', {
          status: response.status,
          data: response.data,
          headers: response.headers
        })
      }
      console.groupEnd()
    }
  },

  // Performance measurement
  measurePerformance: (label: string, fn: () => void) => {
    if (import.meta.env.DEV) {
      console.time(label)
      fn()
      console.timeEnd(label)
    } else {
      fn()
    }
  },

  // Memory usage logging
  logMemoryUsage: () => {
    if (import.meta.env.DEV && 'memory' in performance) {
      const memInfo = (performance as any).memory
      console.log('🧠 Memory Usage:', {
        used: `${Math.round(memInfo.usedJSHeapSize / 1048576)} MB`,
        total: `${Math.round(memInfo.totalJSHeapSize / 1048576)} MB`,
        limit: `${Math.round(memInfo.jsHeapSizeLimit / 1048576)} MB`
      })
    }
  },

  // Component render tracking
  trackRender: (componentName: string) => {
    if (import.meta.env.DEV) {
      console.count(`🔄 ${componentName} rendered`)
    }
  },

  // Environment info
  logEnvironment: () => {
    if (import.meta.env.DEV) {
      console.log('🌍 Environment Info:', {
        mode: import.meta.env.MODE,
        dev: import.meta.env.DEV,
        prod: import.meta.env.PROD,
        baseUrl: import.meta.env.BASE_URL,
        apiUrl: import.meta.env.VITE_API_URL
      })
    }
  }
}

// Performance observer for long tasks
export const initPerformanceObserver = () => {
  if (import.meta.env.DEV && 'PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 50) { // Log tasks longer than 50ms
          console.warn(`🐌 Long task detected: ${entry.name} took ${entry.duration.toFixed(2)}ms`)
        }
      }
    })

    observer.observe({ entryTypes: ['longtask'] })
  }
}

// Error boundary helper
export const reportError = (error: Error, errorInfo?: any) => {
  // In development, log to console
  if (import.meta.env.DEV) {
    console.error('❌ Application Error:', error)
    if (errorInfo) console.error('Error Info:', errorInfo)
  }

  // In production, you could send to error tracking service
  // Example: Sentry, LogRocket, etc.
  if (import.meta.env.PROD) {
    // sendErrorToService(error, errorInfo)
  }
}