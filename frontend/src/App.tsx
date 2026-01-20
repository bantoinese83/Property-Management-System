import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { AuthProvider } from './context/AuthProvider'
import ErrorBoundary from './components/common/ErrorBoundary'
import { Toaster } from './components/ui/sonner'

// Lazy load pages for better performance and code splitting
const LoginPage = lazy(() => import('./pages/LoginPage'))
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const PropertiesPage = lazy(() => import('./pages/PropertiesPage'))
const TenantsPage = lazy(() => import('./pages/TenantsPage'))
const LeasesPage = lazy(() => import('./pages/LeasesPage'))
const MaintenancePage = lazy(() => import('./pages/MaintenancePage'))
const PaymentsPage = lazy(() => import('./pages/PaymentsPage'))
const AccountingPage = lazy(() => import('./pages/AccountingPage'))
const AccountPage = lazy(() => import('./pages/AccountPage'))
const BillingPage = lazy(() => import('./pages/BillingPage'))
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'))
const ReportsPage = lazy(() => import('./pages/ReportsPage'))
const AuditPage = lazy(() => import('./pages/AuditPage'))
const DocumentsPage = lazy(() => import('./pages/DocumentsPage'))

// Loading component for lazy-loaded routes
const PageLoader = () => (
  <div className='flex items-center justify-center min-h-screen'>
    <div className='animate-spin rounded-full h-32 w-32 border-b-2 border-primary'></div>
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
              <Route path='/account' element={<AccountPage />} />
              <Route path='/billing' element={<BillingPage />} />
              <Route path='/notifications' element={<NotificationsPage />} />
              <Route path='/reports' element={<ReportsPage />} />
              <Route path='/audit' element={<AuditPage />} />
              <Route path='/documents' element={<DocumentsPage />} />
              <Route path='/' element={<Navigate to='/dashboard' replace />} />
              <Route path='*' element={<Navigate to='/dashboard' replace />} />
            </Routes>
          </Suspense>
          <Toaster />
        </ErrorBoundary>
      </AuthProvider>
    </Router>
  )
}

export default App
