/**
 * Global test setup for Vitest.
 *
 * Sets up common mocks, utilities, and test environment.
 */

import { beforeAll, afterEach, vi } from 'vitest'
import { cleanup } from '@testing-library/react'

// Mock environment variables
Object.defineProperty(window, 'import.meta', {
  value: {
    env: {
      VITE_API_URL: 'http://localhost:8000/api',
      VITE_APP_ENV: 'test',
      VITE_APP_NAME: 'Property Management System',
    },
  },
})

// Mock window methods that might not be available in test environment
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

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
})

// Mock scrollTo
Object.defineProperty(window, 'scrollTo', {
  value: vi.fn(),
  writable: true,
})

// Mock axios globally
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      interceptors: {
        request: { use: vi.fn(), eject: vi.fn() },
        response: { use: vi.fn(), eject: vi.fn() },
      },
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
    })),
  },
}))

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useLocation: () => ({
      pathname: '/',
      search: '',
      hash: '',
      state: null,
    }),
    useParams: () => ({}),
  }
})

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Home: () => 'HomeIcon',
  Settings: () => 'SettingsIcon',
  User: () => 'UserIcon',
  Building: () => 'BuildingIcon',
  FileText: () => 'FileTextIcon',
  BarChart3: () => 'BarChart3Icon',
  Calendar: () => 'CalendarIcon',
  CheckCircle: () => 'CheckCircleIcon',
  XCircle: () => 'XCircleIcon',
  AlertCircle: () => 'AlertCircleIcon',
  Plus: () => 'PlusIcon',
  Edit: () => 'EditIcon',
  Trash2: () => 'Trash2Icon',
  Search: () => 'SearchIcon',
  Filter: () => 'FilterIcon',
  Download: () => 'DownloadIcon',
  Upload: () => 'UploadIcon',
  Eye: () => 'EyeIcon',
  EyeOff: () => 'EyeOffIcon',
}))

// Mock recharts
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => children,
  LineChart: () => 'LineChart',
  Line: () => 'Line',
  BarChart: () => 'BarChart',
  Bar: () => 'Bar',
  PieChart: () => 'PieChart',
  Pie: () => 'Pie',
  Cell: () => 'Cell',
  XAxis: () => 'XAxis',
  YAxis: () => 'YAxis',
  CartesianGrid: () => 'CartesianGrid',
  Tooltip: () => 'Tooltip',
  Legend: () => 'Legend',
}))

// Mock sonner
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
  },
  Toaster: () => 'Toaster',
}))

// Mock @tanstack/react-query
vi.mock('@tanstack/react-query', () => ({
  QueryClient: vi.fn(() => ({
    invalidateQueries: vi.fn(),
    refetchQueries: vi.fn(),
  })),
  QueryClientProvider: ({ children }: { children: React.ReactNode }) => children,
  useQuery: vi.fn(() => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  })),
  useMutation: vi.fn(() => ({
    mutate: vi.fn(),
    isLoading: false,
    error: null,
  })),
}))

// Setup global test hooks
beforeAll(() => {
  // Global setup
  console.warn('🧪 Test environment initialized')
})

afterEach(() => {
  // Clean up after each test
  cleanup()
  vi.clearAllMocks()

  // Reset localStorage mock
  localStorageMock.clear()
  sessionStorageMock.clear()
})

// Custom test utilities
global.testUtils = {
  // Helper to wait for async operations
  waitForAsync: () => new Promise(resolve => setTimeout(resolve, 0)),

  // Helper to create mock data
  createMockData: (type: string, overrides = {}) => {
    const baseData = {
      id: 1,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    }

    switch (type) {
      case 'property':
        return {
          ...baseData,
          property_name: 'Test Property',
          address: '123 Test St',
          city: 'Test City',
          state: 'TS',
          zip_code: '12345',
          property_type: 'apartment',
          total_units: 5,
          ...overrides,
        }
      case 'tenant':
        return {
          ...baseData,
          first_name: 'John',
          last_name: 'Doe',
          email: 'john.doe@example.com',
          phone: '555-0123',
          ...overrides,
        }
      default:
        return baseData
    }
  },
}

// Type declarations for global test utilities
declare global {
  var testUtils: {
    waitForAsync: () => Promise<void>
    createMockData: (type: string, overrides?: Record<string, unknown>) => unknown
  }
}
