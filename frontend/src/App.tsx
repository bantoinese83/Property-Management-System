import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthProvider'
import ErrorBoundary from './components/common/ErrorBoundary'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PropertiesPage from './pages/PropertiesPage'
import TenantsPage from './pages/TenantsPage'
import LeasesPage from './pages/LeasesPage'
import MaintenancePage from './pages/MaintenancePage'
import PaymentsPage from './pages/PaymentsPage'

import './App.css'

function App() {
  return (
    <Router>
      <AuthProvider>
        <ErrorBoundary
          showErrorDetails={process.env.NODE_ENV === 'development'}
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
            <Route path='/' element={<Navigate to='/dashboard' replace />} />
            <Route path='*' element={<Navigate to='/dashboard' replace />} />
          </Routes>
        </ErrorBoundary>
      </AuthProvider>
    </Router>
  )
}

export default App
