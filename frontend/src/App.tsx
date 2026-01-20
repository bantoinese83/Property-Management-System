import { Suspense, lazy } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthProvider'
import ErrorBoundary from './components/common/ErrorBoundary'
import { LoadingSpinner } from './components/common'
import './App.css'

// Lazy load pages for better performance
const LoginPage = lazy(() => import('./pages/LoginPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const PropertiesPage = lazy(() => import('./pages/PropertiesPage'))
const TenantsPage = lazy(() => import('./pages/TenantsPage'))
const LeasesPage = lazy(() => import('./pages/LeasesPage'))
const MaintenancePage = lazy(() => import('./pages/MaintenancePage'))
const PaymentsPage = lazy(() => import('./pages/PaymentsPage'))
const AccountingPage = lazy(() => import('./pages/AccountingPage'))

// Loading fallback component
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="text-center">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-muted-foreground">Loading page...</p>
    </div>
  </div>
)

function App() {
  return (
    <Router>
      <AuthProvider>
        <ErrorBoundary
          showErrorDetails={import.meta.env.DEV}
          maxRetries={3}
          onError={(error, errorInfo) => {
            // Log to console in development, could send to error tracking service in production
            console.error('Application Error:', error, errorInfo)
          }}
        >
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path='/login' element={<LoginPage />} />
              <Route path='/dashboard' element={<DashboardPage />} />
              <Route path='/properties' element={<PropertiesPage />} />
              <Route path='/tenants' element={<TenantsPage />} />
              <Route path='/leases' element={<LeasesPage />} />
              <Route path='/maintenance' element={<MaintenancePage />} />
              <Route path='/payments' element={<PaymentsPage />} />
              <Route path='/accounting' element={<AccountingPage />} />
              <Route path='/' element={<Navigate to='/dashboard' replace />} />
              <Route path='*' element={<Navigate to='/dashboard' replace />} />
            </Routes>
          </Suspense>
        </ErrorBoundary>
      </AuthProvider>
    </Router>
  )
}

export default App
