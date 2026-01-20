import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthProvider'
import ErrorBoundary from './components/common/ErrorBoundary'
import { Toaster } from './components/ui/sonner'

// Import pages directly (lazy loading causes path alias resolution issues in development)
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PropertiesPage from './pages/PropertiesPage'
import TenantsPage from './pages/TenantsPage'
import LeasesPage from './pages/LeasesPage'
import MaintenancePage from './pages/MaintenancePage'
import PaymentsPage from './pages/PaymentsPage'
import AccountingPage from './pages/AccountingPage'
import AccountPage from './pages/AccountPage'
import BillingPage from './pages/BillingPage'
import NotificationsPage from './pages/NotificationsPage'
import ReportsPage from './pages/ReportsPage'
import AuditPage from './pages/AuditPage'
import DocumentsPage from './pages/DocumentsPage'

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
          <Toaster />
        </ErrorBoundary>
      </AuthProvider>
    </Router>
  )
}

export default App
