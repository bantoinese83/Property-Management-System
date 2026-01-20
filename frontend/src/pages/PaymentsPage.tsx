import React, { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import type { RentPayment } from '../types/models'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { Input } from '../components/common/Input'
import { LoadingSpinner, ErrorMessage } from '../components/common'
import { DollarSign, CheckCircle, AlertTriangle, Clock, TrendingUp } from 'lucide-react'

interface PaymentsResponse {
  results: RentPayment[]
  count: number
  next?: string
  previous?: string
}

const PaymentsPage: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [paymentMessage, setPaymentMessage] = useState<{
    type: 'success' | 'error'
    text: string
  } | null>(null)

  const { data, loading, error, refetch } = useApi<PaymentsResponse>(
    `${API_ENDPOINTS.PAYMENTS.LIST}?search=${searchTerm}&status=${statusFilter}`
  )

  const payments = data?.results || []

  // Handle URL parameters for payment status
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    if (params.get('success')) {
      setPaymentMessage({ type: 'success', text: 'Payment completed successfully!' })
      navigate(location.pathname, { replace: true })
      refetch()
    } else if (params.get('canceled')) {
      setPaymentMessage({ type: 'error', text: 'Payment was canceled.' })
      navigate(location.pathname, { replace: true })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search, navigate, refetch])

  const handlePayNow = async (paymentId: number) => {
    try {
      const response = await fetch(API_ENDPOINTS.PAYMENTS.CREATE_STRIPE_SESSION(paymentId), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          success_url: `${window.location.origin}/payments?success=true&session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${window.location.origin}/payments?canceled=true`,
        }),
      })

      const result = await response.json()
      if (result.url) {
        window.location.assign(result.url)
      } else {
        alert(result.error || 'Failed to initiate payment')
      }
    } catch (err) {
      console.error('Error initiating payment:', err)
      alert('An error occurred. Please try again.')
    }
  }

  if (loading && !payments.length) {
    return (
      <SidebarProvider
        style={{
          "--sidebar-width": "280px",
          "--header-height": "60px",
        } as React.CSSProperties}
      >
        <AppSidebar variant="inset" />
        <SidebarInset>
          <SiteHeader />
          <div className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Payments</h1>
                <p className="text-muted-foreground">
                  Track and manage rent payments
                </p>
              </div>
            </div>
            <div className="flex flex-1 items-center justify-center">
              <LoadingSpinner size="lg" />
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
  }

  if (error) {
    return (
      <SidebarProvider
        style={{
          "--sidebar-width": "280px",
          "--header-height": "60px",
        } as React.CSSProperties}
      >
        <AppSidebar variant="inset" />
        <SidebarInset>
          <SiteHeader />
          <div className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Payments</h1>
                <p className="text-muted-foreground">
                  Track and manage rent payments
                </p>
              </div>
            </div>
            <div className="flex flex-1 items-center justify-center">
              <ErrorMessage message={error.message} title='Failed to load payments' />
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
  }

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'paid':
        return 'success'
      case 'pending':
        return 'warning'
      case 'overdue':
        return 'danger'
      case 'failed':
        return 'danger'
      default:
        return 'default'
    }
  }

  // Calculate stats
  const totalPayments = payments.length
  const paidPayments = payments.filter(p => p.status === 'paid').length
  const pendingPayments = payments.filter(p => p.status === 'pending').length
  const overduePayments = payments.filter(p => p.status === 'overdue').length
  const totalAmount = payments.reduce((sum, p) => sum + parseFloat(p.total_amount), 0)

  return (
    <SidebarProvider
      style={{
        "--sidebar-width": "280px",
        "--header-height": "60px",
      } as React.CSSProperties}
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
          {/* Header Section */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Payments</h1>
              <p className="text-muted-foreground">
                Track and manage rent payments
              </p>
            </div>
          </div>

          {/* Success/Error Messages */}
          {paymentMessage && (
            <div className={`rounded-lg border p-4 ${
              paymentMessage.type === 'success'
                ? 'border-green-200 bg-green-50 text-green-800'
                : 'border-red-200 bg-red-50 text-red-800'
            }`}>
              <div className="flex items-center justify-between">
                <p>{paymentMessage.text}</p>
                <button
                  onClick={() => setPaymentMessage(null)}
                  className="text-sm hover:opacity-75"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Payments</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl">
                    {totalPayments}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <DollarSign className="h-5 w-5 text-primary" />
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Paid</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl text-green-600">
                    {paidPayments}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Pending</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl text-yellow-600">
                    {pendingPayments}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-yellow-100">
                  <Clock className="h-5 w-5 text-yellow-600" />
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Overdue</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl text-red-600">
                    {overduePayments}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-100">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Amount</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl">
                    ${totalAmount.toFixed(2)}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <TrendingUp className="h-5 w-5 text-primary" />
                </div>
              </div>
            </div>
          </div>

          {/* Filters Section */}
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-1 gap-4">
              <div className="flex-1">
                <Input
                  type="text"
                  placeholder="Search by tenant name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="max-w-sm"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="flex h-10 w-full max-w-[200px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="paid">Paid</option>
                <option value="overdue">Overdue</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>

          {/* Payments Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {payments.length === 0 ? (
              <div className="col-span-full rounded-lg border border-dashed p-8 text-center">
                <DollarSign className="mx-auto h-12 w-12 text-muted-foreground" />
                <h3 className="mt-2 text-sm font-medium">No payments found</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Get started by creating your first payment.
                </p>
              </div>
            ) : (
              payments.map((payment) => (
                <Card key={payment.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-sm text-foreground">
                        {payment.lease_property_name}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {payment.lease_tenant_name}
                      </p>
                    </div>
                    <Badge variant={getStatusVariant(payment.status)} className="text-xs">
                      {payment.status.toUpperCase()}
                    </Badge>
                  </div>

                  <div className="mt-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Amount</span>
                      <span className="font-semibold">${payment.total_amount}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Due Date</span>
                      <span className="text-sm">{new Date(payment.due_date).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Method</span>
                      <span className="text-sm capitalize">{payment.payment_method.replace('_', ' ')}</span>
                    </div>
                  </div>

                  {payment.status === 'paid' && payment.processed_at && (
                    <div className="mt-4 rounded-lg bg-green-50 p-3 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-green-700">Paid on</span>
                        <span className="font-medium text-green-700">
                          {new Date(payment.processed_at).toLocaleDateString()}
                        </span>
                      </div>
                      {payment.transaction_id && (
                        <div className="mt-1 flex items-center justify-between">
                          <span className="text-green-600">Ref:</span>
                          <span className="font-mono text-xs text-green-600 truncate ml-2">
                            {payment.transaction_id}
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {(payment.status === 'pending' || payment.status === 'overdue') && (
                    <div className="mt-4">
                      <Button
                        variant="primary"
                        className="w-full"
                        onClick={() => handlePayNow(payment.id)}
                      >
                        Pay Now with Stripe
                      </Button>
                    </div>
                  )}
                </Card>
              ))
            )}
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default PaymentsPage
