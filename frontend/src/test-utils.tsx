/* eslint-disable react-refresh/only-export-components */
/**
 * Test utilities for React components and hooks.
 *
 * Provides reusable test utilities, mocks, and helpers for consistent testing.
 */

import React, { type ReactElement } from 'react'
import { render, type RenderOptions } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import '@testing-library/jest-dom'

// Mock implementations
export const mockAxios = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
}

// Test wrapper components
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  )
}

// Custom render function
const customRender = (ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) =>
  render(ui, { wrapper: TestWrapper, ...options })

// Re-export everything
export * from '@testing-library/react'
export { customRender as render }

// Test data generators
export const createMockProperty = (overrides = {}) => ({
  id: 1,
  property_name: 'Test Property',
  address: '123 Test St',
  city: 'Test City',
  state: 'TS',
  zip_code: '12345',
  property_type: 'apartment',
  total_units: 5,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
})

export const createMockTenant = (overrides = {}) => ({
  id: 1,
  first_name: 'John',
  last_name: 'Doe',
  email: 'john.doe@example.com',
  phone: '555-0123',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
})

export const createMockLease = (overrides = {}) => ({
  id: 1,
  property_obj: createMockProperty(),
  tenant: createMockTenant(),
  lease_start_date: '2024-01-01',
  lease_end_date: '2024-12-31',
  monthly_rent: '2000.00',
  deposit_amount: '2000.00',
  status: 'active',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
})

// Mock API responses
export const mockApiResponse = {
  success: (data: unknown) => ({
    data,
    status: 200,
    statusText: 'OK',
  }),
  error: (message: string, status = 400) => ({
    response: {
      data: { message },
      status,
    },
  }),
}

// Test helpers
export const waitForLoadingToFinish = async () => {
  // Wait for any loading states to finish
  await new Promise(resolve => setTimeout(resolve, 0))
}

export const mockConsoleError = () => {
  const originalError = console.error
  beforeAll(() => {
    console.error = vi.fn()
  })
  afterAll(() => {
    console.error = originalError
  })
}

export const mockLocalStorage = () => {
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  }

  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
  })

  return localStorageMock
}

export const mockMatchMedia = () => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })
}

// Form testing helpers
export const fillForm = async (
  user: ReturnType<typeof userEvent.setup>,
  form: HTMLElement,
  data: Record<string, string>
) => {
  for (const [name, value] of Object.entries(data)) {
    const input = form.querySelector(`[name="${name}"]`) as HTMLInputElement
    if (input) {
      await user.clear(input)
      await user.type(input, value)
    }
  }
}

export const submitForm = async (user: ReturnType<typeof userEvent.setup>, form: HTMLElement) => {
  const submitButton = form.querySelector('button[type="submit"], input[type="submit"]')
  if (submitButton) {
    await user.click(submitButton)
  }
}

// API testing helpers
export const mockApiCall = (method: string, _url: string, response: unknown) => {
  mockAxios[method as keyof typeof mockAxios].mockResolvedValueOnce(response)
}

export const mockApiError = (method: string, _url: string, error: unknown) => {
  mockAxios[method as keyof typeof mockAxios].mockRejectedValueOnce(error)
}

// Performance testing helpers
export const measureRenderTime = async (component: ReactElement) => {
  const startTime = performance.now()
  const { container } = render(component)
  await waitForLoadingToFinish()
  const endTime = performance.now()

  return {
    renderTime: endTime - startTime,
    container,
  }
}

// Accessibility testing helpers
export const checkAccessibility = (container: HTMLElement) => {
  // Basic accessibility checks
  const images = container.querySelectorAll('img')
  const imagesWithoutAlt = Array.from(images).filter(img => !img.alt)

  const buttons = container.querySelectorAll('button')
  const buttonsWithoutAriaLabel = Array.from(buttons).filter(
    button => !button.getAttribute('aria-label') && !button.textContent?.trim()
  )

  return {
    imagesWithoutAlt: imagesWithoutAlt.length,
    buttonsWithoutAriaLabel: buttonsWithoutAriaLabel.length,
    totalIssues: imagesWithoutAlt.length + buttonsWithoutAriaLabel.length,
  }
}

// Setup file for vitest
export const setupTestEnvironment = () => {
  // Mock environment variables
  vi.stubEnv('VITE_API_URL', 'http://localhost:8000/api')

  // Mock window methods
  Object.defineProperty(window, 'scrollTo', {
    value: vi.fn(),
    writable: true,
  })

  // Mock ResizeObserver
  ;(globalThis as unknown as { ResizeObserver: unknown }).ResizeObserver = vi
    .fn()
    .mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }))

  // Mock IntersectionObserver
  ;(globalThis as unknown as { IntersectionObserver: unknown }).IntersectionObserver = vi
    .fn()
    .mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }))

  // Mock matchMedia
  mockMatchMedia()
}

// Custom matchers
declare module 'vitest' {
  interface Assertion {
    toHaveNoViolations(): void
    toBeAccessible(): void
  }
}

// Custom matchers - temporarily disabled due to type issues
// expect.extend({
//   toHaveNoViolations(received) {
//     const accessibility = checkAccessibility(received)
//     const pass = accessibility.totalIssues === 0

//     return {
//       pass,
//       message: () =>
//         pass
//           ? 'Expected element to have accessibility violations'
//           : `Found ${accessibility.totalIssues} accessibility issues: ${accessibility.imagesWithoutAlt} images without alt text, ${accessibility.buttonsWithoutAriaLabel} buttons without labels`,
//     }
//   },

//   toBeAccessible(received) {
//     return this.toHaveNoViolations(received)
//   },
// })

// setupTestEnvironment is exported as a const above
