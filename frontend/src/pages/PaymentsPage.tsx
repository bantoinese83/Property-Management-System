import React, { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import type { RentPayment } from '../types/models'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { Badge } from '../components/common/Badge'
import { LoadingSpinner, ErrorMessage } from '../components/common'
import '../styles/pages/PaymentsPage.css'

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
      <div className='flex h-[80vh] items-center justify-center'>
        <LoadingSpinner size='lg' />
      </div>
    )
  }

  if (error) {
    return (
      <div className='flex h-[80vh] items-center justify-center'>
        <ErrorMessage message={error.message} title='Failed to load payments' />
      </div>
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

  return (
    <div className='payments-page'>
      <div className='payments-header'>
        <div>
          <h1>Payments</h1>
          <p>Track and manage rent payments</p>
        </div>
      </div>

      {paymentMessage && (
        <div className={`payment-alert ${paymentMessage.type}`}>
          {paymentMessage.text}
          <button onClick={() => setPaymentMessage(null)}>&times;</button>
        </div>
      )}

      <div className='payments-filters'>
        <div className='filter-group'>
          <input
            type='text'
            placeholder='Search by tenant name...'
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className='search-input'
          />
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            className='status-select'
          >
            <option value=''>All Statuses</option>
            <option value='pending'>Pending</option>
            <option value='paid'>Paid</option>
            <option value='overdue'>Overdue</option>
          </select>
        </div>
      </div>

      <div className='payments-grid'>
        {payments.length === 0 ? (
          <div className='no-payments'>No payments found.</div>
        ) : (
          payments.map(payment => (
            <Card
              key={payment.id}
              title={payment.lease_property_name}
              subtitle={payment.lease_tenant_name}
              className='payment-card'
            >
              <div className='payment-info'>
                <div className='payment-details'>
                  <div className='payment-row'>
                    <span>Amount:</span>
                    <span className='font-bold'>${payment.total_amount}</span>
                  </div>
                  <div className='payment-row'>
                    <span>Due Date:</span>
                    <span>{new Date(payment.due_date).toLocaleDateString()}</span>
                  </div>
                  <div className='payment-row'>
                    <span>Status:</span>
                    <Badge variant={getStatusVariant(payment.status)}>
                      {payment.status.toUpperCase()}
                    </Badge>
                  </div>
                </div>

                {payment.status === 'pending' || payment.status === 'overdue' ? (
                  <div className='payment-actions'>
                    <Button
                      variant='primary'
                      className='w-full mt-4'
                      onClick={() => handlePayNow(payment.id)}
                    >
                      Pay Now with Stripe
                    </Button>
                  </div>
                ) : (
                  payment.status === 'paid' && (
                    <div className='payment-receipt mt-4 p-2 bg-gray-50 rounded text-sm'>
                      <div className='flex justify-between'>
                        <span>Paid On:</span>
                        <span>
                          {payment.processed_at
                            ? new Date(payment.processed_at).toLocaleDateString()
                            : 'N/A'}
                        </span>
                      </div>
                      {payment.transaction_id && (
                        <div className='flex justify-between mt-1'>
                          <span>Ref:</span>
                          <span className='text-xs text-gray-500 truncate ml-2'>
                            {payment.transaction_id}
                          </span>
                        </div>
                      )}
                    </div>
                  )
                )}
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

export default PaymentsPage
