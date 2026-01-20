import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/common/Badge'
import { LoadingSpinner } from '../components/common'
import { toast } from 'sonner'
import {
  CreditCard,
  Calendar,
  DollarSign,
  CheckCircle,
  XCircle,
  Download,
  Plus,
  AlertTriangle,
} from 'lucide-react'

interface SubscriptionPlan {
  id: number
  name: string
  plan_type: string
  description: string
  price: string
  currency: string
  interval: string
  max_properties: number
  max_tenants: number
  max_users: number
  storage_limit_mb: number
  is_active: boolean
}

interface Subscription {
  id: string
  plan: number
  plan_name: string
  plan_price: string
  status: string
  current_period_start: string
  current_period_end: string
  cancel_at_period_end: boolean
  is_active: boolean
  days_until_expiry: number
}

interface PaymentMethod {
  id: number
  method_type: string
  last4: string
  brand: string
  exp_month: number
  exp_year: number
  bank_name: string
  account_last4: string
  is_default: boolean
  display_name: string
  created_at: string
}

interface Invoice {
  id: string
  amount: string
  currency: string
  status: string
  invoice_date: string
  due_date?: string
  paid_at?: string
  description: string
}

const BillingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'plans' | 'payment-methods' | 'invoices'>(
    'overview'
  )

  const { data: plansData, loading: plansLoading } = useApi<
    { results: SubscriptionPlan[]; count: number } | SubscriptionPlan[]
  >(API_ENDPOINTS.BILLING.PLANS)

  const { data: subscriptionData, loading: subscriptionLoading } = useApi<{
    results: Subscription[]
    count: number
  }>(API_ENDPOINTS.BILLING.SUBSCRIPTIONS)

  const { data: paymentMethodsData, loading: paymentMethodsLoading } = useApi<{
    results: PaymentMethod[]
    count: number
  }>(API_ENDPOINTS.BILLING.PAYMENT_METHODS)

  const { data: invoicesData, loading: invoicesLoading } = useApi<{
    results: Invoice[]
    count: number
  }>(API_ENDPOINTS.BILLING.INVOICES)

  const currentSubscription = subscriptionData?.results?.[0]

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'past_due':
        return 'bg-red-100 text-red-800'
      case 'canceled':
        return 'bg-gray-100 text-gray-800'
      case 'trialing':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-yellow-100 text-yellow-800'
    }
  }

  const formatCurrency = (amount: string | number, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(Number(amount))
  }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'plans', label: 'Plans' },
    { id: 'payment-methods', label: 'Payment Methods' },
    { id: 'invoices', label: 'Invoices' },
  ]

  return (
    <SidebarProvider
      style={
        {
          '--sidebar-width': '280px',
          '--header-height': '60px',
        } as React.CSSProperties
      }
    >
      <AppSidebar variant='inset' />
      <SidebarInset>
        <SiteHeader />
        <div className='flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6'>
          {/* Header */}
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold tracking-tight'>Billing & Subscriptions</h1>
              <p className='text-muted-foreground'>
                Manage your subscription, billing, and payment methods
              </p>
            </div>
          </div>

          {/* Tabs */}
          <div className='flex space-x-1 bg-muted p-1 rounded-lg w-fit'>
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as 'overview' | 'plans' | 'payment-methods' | 'invoices')}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  activeTab === tab.id
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className='grid gap-6 md:grid-cols-2 lg:grid-cols-3'>
              {/* Current Subscription */}
              <Card className='md:col-span-2'>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2'>
                    <CreditCard className='h-5 w-5' />
                    Current Subscription
                  </CardTitle>
                  <CardDescription>Your current plan and billing information</CardDescription>
                </CardHeader>
                <CardContent>
                  {subscriptionLoading ? (
                    <LoadingSpinner size='sm' />
                  ) : currentSubscription ? (
                    <div className='space-y-4'>
                      <div className='flex items-center justify-between'>
                        <div>
                          <h3 className='text-lg font-semibold'>{currentSubscription.plan_name}</h3>
                          <p className='text-sm text-muted-foreground'>
                            {formatCurrency(currentSubscription.plan_price)}/month
                          </p>
                        </div>
                        <Badge className={getStatusColor(currentSubscription.status)}>
                          {currentSubscription.status}
                        </Badge>
                      </div>

                      <div className='grid grid-cols-2 gap-4 pt-4'>
                        <div className='flex items-center gap-2'>
                          <Calendar className='h-4 w-4 text-muted-foreground' />
                          <div>
                            <p className='text-xs text-muted-foreground'>Current Period</p>
                            <p className='text-sm font-medium'>
                              {new Date(
                                currentSubscription.current_period_start
                              ).toLocaleDateString()}{' '}
                              -{' '}
                              {new Date(
                                currentSubscription.current_period_end
                              ).toLocaleDateString()}
                            </p>
                          </div>
                        </div>

                        {currentSubscription.days_until_expiry > 0 && (
                          <div className='flex items-center gap-2'>
                            <AlertTriangle className='h-4 w-4 text-muted-foreground' />
                            <div>
                              <p className='text-xs text-muted-foreground'>Days Remaining</p>
                              <p className='text-sm font-medium'>
                                {currentSubscription.days_until_expiry} days
                              </p>
                            </div>
                          </div>
                        )}
                      </div>

                      {currentSubscription.cancel_at_period_end && (
                        <div className='flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md'>
                          <AlertTriangle className='h-4 w-4 text-yellow-600' />
                          <p className='text-sm text-yellow-800'>
                            Your subscription will be canceled at the end of the current billing
                            period.
                          </p>
                        </div>
                      )}

                      <div className='flex gap-2 pt-4'>
                        <Button
                          variant='outline'
                          size='sm'
                          onClick={() =>
                            toast.info('Plan change feature coming soon!', {
                              description:
                                'You will be able to upgrade or downgrade your subscription plan.',
                            })
                          }
                        >
                          Change Plan
                        </Button>
                        <Button
                          variant='outline'
                          size='sm'
                          onClick={() =>
                            toast.info(
                              currentSubscription.cancel_at_period_end
                                ? 'Subscription reactivation coming soon!'
                                : 'Subscription cancellation coming soon!',
                              {
                                description: currentSubscription.cancel_at_period_end
                                  ? 'You will be able to reactivate your cancelled subscription.'
                                  : 'You will be able to cancel your subscription at the end of the billing period.',
                              }
                            )
                          }
                        >
                          {currentSubscription.cancel_at_period_end
                            ? 'Reactivate'
                            : 'Cancel Subscription'}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className='text-center py-8'>
                      <CreditCard className='h-12 w-12 text-muted-foreground mx-auto mb-4' />
                      <h3 className='text-lg font-medium mb-2'>No Active Subscription</h3>
                      <p className='text-sm text-muted-foreground mb-4'>
                        Choose a plan to get started with our services.
                      </p>
                      <Button onClick={() => setActiveTab('plans')}>View Plans</Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Quick Stats */}
              <Card>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2'>
                    <DollarSign className='h-5 w-5' />
                    Billing Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className='space-y-4'>
                  <div className='flex justify-between'>
                    <span className='text-sm text-muted-foreground'>Next billing date</span>
                    <span className='text-sm font-medium'>
                      {currentSubscription
                        ? new Date(currentSubscription.current_period_end).toLocaleDateString()
                        : 'N/A'}
                    </span>
                  </div>

                  <div className='flex justify-between'>
                    <span className='text-sm text-muted-foreground'>Amount due</span>
                    <span className='text-sm font-medium'>
                      {currentSubscription
                        ? formatCurrency(currentSubscription.plan_price)
                        : '$0.00'}
                    </span>
                  </div>

                  <div className='flex justify-between'>
                    <span className='text-sm text-muted-foreground'>Payment method</span>
                    <span className='text-sm font-medium'>
                      {paymentMethodsData?.results?.find(pm => pm.is_default)?.display_name ||
                        'None'}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === 'plans' && (
            <div className='grid gap-6 md:grid-cols-2 lg:grid-cols-3'>
              {plansLoading ? (
                <div className='col-span-full flex justify-center py-8'>
                  <LoadingSpinner size='lg' />
                </div>
              ) : (
                (Array.isArray(plansData) ? plansData : plansData?.results || [])?.map((plan: SubscriptionPlan) => (
                  <Card
                    key={plan.id}
                    className={`relative ${currentSubscription?.plan === plan.id ? 'ring-2 ring-primary' : ''}`}
                  >
                    {currentSubscription?.plan === plan.id && (
                      <div className='absolute -top-3 left-1/2 transform -translate-x-1/2'>
                        <Badge className='bg-primary text-primary-foreground'>Current Plan</Badge>
                      </div>
                    )}

                    <CardHeader>
                      <CardTitle>{plan.name}</CardTitle>
                      <CardDescription>{plan.description}</CardDescription>
                      <div className='flex items-baseline gap-1'>
                        <span className='text-3xl font-bold'>{formatCurrency(plan.price)}</span>
                        <span className='text-sm text-muted-foreground'>/{plan.interval}</span>
                      </div>
                    </CardHeader>

                    <CardContent className='space-y-4'>
                      <div className='space-y-2'>
                        <div className='flex justify-between text-sm'>
                          <span>Properties</span>
                          <span>
                            {plan.max_properties === -1 ? 'Unlimited' : plan.max_properties}
                          </span>
                        </div>
                        <div className='flex justify-between text-sm'>
                          <span>Tenants</span>
                          <span>{plan.max_tenants === -1 ? 'Unlimited' : plan.max_tenants}</span>
                        </div>
                        <div className='flex justify-between text-sm'>
                          <span>Users</span>
                          <span>{plan.max_users === -1 ? 'Unlimited' : plan.max_users}</span>
                        </div>
                        <div className='flex justify-between text-sm'>
                          <span>Storage</span>
                          <span>{plan.storage_limit_mb}MB</span>
                        </div>
                      </div>

                      <Button
                        className='w-full'
                        variant={currentSubscription?.plan === plan.id ? 'outline' : 'default'}
                        disabled={currentSubscription?.plan === plan.id}
                        onClick={() => {
                          if (currentSubscription?.plan === plan.id) {
                            toast.info('This is your current plan', {
                              description: "You're already subscribed to this plan.",
                            })
                          } else {
                            toast.info('Plan selection coming soon!', {
                              description: `You will be able to subscribe to the ${plan.name} plan.`,
                            })
                          }
                        }}
                      >
                        {currentSubscription?.plan === plan.id ? 'Current Plan' : 'Select Plan'}
                      </Button>
                    </CardContent>
                  </Card>
                )) || (
                  <div className='col-span-full text-center py-8'>
                    <p className='text-muted-foreground'>No plans available at the moment.</p>
                  </div>
                )
              )}
            </div>
          )}

          {activeTab === 'payment-methods' && (
            <Card>
              <CardHeader>
                <div className='flex items-center justify-between'>
                  <div>
                    <CardTitle className='flex items-center gap-2'>
                      <CreditCard className='h-5 w-5' />
                      Payment Methods
                    </CardTitle>
                    <CardDescription>Manage your payment methods for billing</CardDescription>
                  </div>
                  <Button
                    onClick={() =>
                      toast.info('Add payment method feature coming soon!', {
                        description:
                          'You will be able to add credit cards, debit cards, and bank accounts for billing.',
                      })
                    }
                  >
                    <Plus className='h-4 w-4 mr-2' />
                    Add Payment Method
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {paymentMethodsLoading ? (
                  <LoadingSpinner size='sm' />
                ) : paymentMethodsData?.results?.length ? (
                  <div className='space-y-4'>
                    {paymentMethodsData.results.map(method => (
                      <div
                        key={method.id}
                        className='flex items-center justify-between p-4 border rounded-lg'
                      >
                        <div className='flex items-center gap-3'>
                          <CreditCard className='h-5 w-5 text-muted-foreground' />
                          <div>
                            <p className='font-medium'>{method.display_name}</p>
                            <p className='text-sm text-muted-foreground'>
                              Added {new Date(method.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          {method.is_default && <Badge variant='outline'>Default</Badge>}
                        </div>
                        <div className='flex gap-2'>
                          {!method.is_default && (
                            <Button
                              variant='outline'
                              size='sm'
                              onClick={() =>
                                toast.info('Set default payment method coming soon!', {
                                  description:
                                    'You will be able to change your default payment method.',
                                })
                              }
                            >
                              Set as Default
                            </Button>
                          )}
                          <Button
                            variant='outline'
                            size='sm'
                            onClick={() =>
                              toast.info('Edit payment method coming soon!', {
                                description:
                                  'You will be able to update your payment method details.',
                              })
                            }
                          >
                            Edit
                          </Button>
                          <Button
                            variant='outline'
                            size='sm'
                            onClick={() =>
                              toast.info('Remove payment method coming soon!', {
                                description:
                                  'You will be able to remove payment methods from your account.',
                              })
                            }
                          >
                            Remove
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className='text-center py-8'>
                    <CreditCard className='h-12 w-12 text-muted-foreground mx-auto mb-4' />
                    <h3 className='text-lg font-medium mb-2'>No Payment Methods</h3>
                    <p className='text-sm text-muted-foreground mb-4'>
                      Add a payment method to manage your billing.
                    </p>
                    <Button>
                      <Plus className='h-4 w-4 mr-2' />
                      Add Payment Method
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {activeTab === 'invoices' && (
            <Card>
              <CardHeader>
                <CardTitle className='flex items-center gap-2'>
                  <Download className='h-5 w-5' />
                  Invoices
                </CardTitle>
                <CardDescription>View and download your billing invoices</CardDescription>
              </CardHeader>
              <CardContent>
                {invoicesLoading ? (
                  <LoadingSpinner size='sm' />
                ) : invoicesData?.results?.length ? (
                  <div className='space-y-4'>
                    {invoicesData.results.map(invoice => (
                      <div
                        key={invoice.id}
                        className='flex items-center justify-between p-4 border rounded-lg'
                      >
                        <div className='flex items-center gap-3'>
                          <div
                            className={`p-2 rounded-full ${invoice.status === 'paid' ? 'bg-green-100' : 'bg-yellow-100'}`}
                          >
                            {invoice.status === 'paid' ? (
                              <CheckCircle className='h-4 w-4 text-green-600' />
                            ) : (
                              <XCircle className='h-4 w-4 text-yellow-600' />
                            )}
                          </div>
                          <div>
                            <p className='font-medium'>Invoice #{invoice.id.slice(-8)}</p>
                            <p className='text-sm text-muted-foreground'>
                              {new Date(invoice.invoice_date).toLocaleDateString()}
                            </p>
                            {invoice.description && (
                              <p className='text-xs text-muted-foreground'>{invoice.description}</p>
                            )}
                          </div>
                        </div>
                        <div className='flex items-center gap-4'>
                          <div className='text-right'>
                            <p className='font-medium'>{formatCurrency(invoice.amount)}</p>
                            <Badge className={getStatusColor(invoice.status)}>
                              {invoice.status}
                            </Badge>
                          </div>
                          <Button
                            variant='outline'
                            size='sm'
                            onClick={() =>
                              toast.info('Invoice download coming soon!', {
                                description:
                                  'You will be able to download PDF copies of your invoices.',
                              })
                            }
                          >
                            <Download className='h-4 w-4 mr-2' />
                            Download
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className='text-center py-8'>
                    <Download className='h-12 w-12 text-muted-foreground mx-auto mb-4' />
                    <h3 className='text-lg font-medium mb-2'>No Invoices</h3>
                    <p className='text-sm text-muted-foreground'>
                      Your invoices will appear here once you have billing activity.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default BillingPage
