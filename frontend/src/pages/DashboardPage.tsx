import React from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { AppSidebar } from '../components/app-sidebar'
import { ChartAreaInteractive } from '../components/chart-area-interactive'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { ErrorMessage, Badge } from '../components/common'
import {
  Home,
  Building2,
  BarChart3,
  DollarSign,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Wrench,
  Users,
  Activity
} from 'lucide-react'

interface DashboardAnalytics {
  summary: {
    total_properties: number
    total_units: number
    occupied_units: number
    vacant_units: number
    average_occupancy: number
    total_monthly_income: string
    total_annual_income: string
    monthly_collections: string
    total_outstanding: string
    active_leases: number
    expiring_leases: number
    open_maintenance: number
    urgent_maintenance: number
  }
  charts: {
    monthly_revenue: Array<{
      month: string
      revenue: number
      collections: number
    }>
    property_types: Record<
      string,
      {
        count: number
        total_units: number
        occupied_units: number
        monthly_income: number
      }
    >
  }
  recent_activity: Array<{
    type: 'payment' | 'maintenance'
    description: string
    amount?: string
    priority?: string
    date: string
    property: string
  }>
}

// Using real property data for the table instead of sample data

const DashboardPage: React.FC = () => {
  const { data, loading, error } = useApi<DashboardAnalytics>(
    `${API_ENDPOINTS.PROPERTIES.LIST}dashboard_analytics/`
  )

  // Additional API calls for enhanced dashboard
  const { data: accountingSummary } = useApi<{
    summary: {
      total_income: string
      total_expenses: string
      net_income: string
      transaction_count: number
    }
  }>(`${API_ENDPOINTS.ACCOUNTING.TRANSACTIONS.LIST}summary/`)

  const { data: overduePayments } = useApi<{ results: any[] }>(
    `${API_ENDPOINTS.PAYMENTS.LIST}overdue/`
  )

  const { data: pendingMaintenance } = useApi<{ results: any[] }>(
    `${API_ENDPOINTS.MAINTENANCE.LIST}?status=open&priority=urgent`
  )

  if (loading) {
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
            {/* Loading skeleton for metrics cards */}
            <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-4'>
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className='h-32 rounded-lg bg-muted animate-pulse' />
              ))}
            </div>

            {/* Loading skeleton for chart */}
            <div className='h-96 rounded-lg bg-muted animate-pulse' />

            {/* Loading skeleton for table */}
            <div className='h-64 rounded-lg bg-muted animate-pulse' />
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
  }

  if (error) {
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
          <div className='flex flex-1 items-center justify-center p-4 lg:p-6'>
            <ErrorMessage message={error.message} title='Failed to load dashboard' />
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
  }

  if (!data) {
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
          <div className='flex flex-1 items-center justify-center p-4 lg:p-6'>
            <ErrorMessage
              message='No analytics data was returned from the server.'
              title='No Data Available'
            />
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
  }

  const { summary, charts } = data

  const formatCurrency = (amount: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(parseFloat(amount))
  }

  const formatPercent = (value: number) => {
    return `${value.toFixed(1)}%`
  }

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
          {/* Alerts Section */}
          {((overduePayments?.results?.length ?? 0) > 0 || (pendingMaintenance?.results?.length ?? 0) > 0) && (
            <div className='rounded-lg border border-amber-200 bg-amber-50 p-4'>
              <div className='flex items-start gap-3'>
                <AlertTriangle className='h-5 w-5 text-amber-600 mt-0.5' />
                <div className='flex-1'>
                  <h4 className='font-medium text-amber-800'>Attention Required</h4>
                  <div className='mt-2 space-y-1'>
                    {(overduePayments?.results?.length ?? 0) > 0 && (
                      <p className='text-sm text-amber-700'>
                        {overduePayments?.results?.length ?? 0} overdue payment{(overduePayments?.results?.length ?? 0) !== 1 ? 's' : ''}
                      </p>
                    )}
                    {(pendingMaintenance?.results?.length ?? 0) > 0 && (
                      <p className='text-sm text-amber-700'>
                        {pendingMaintenance?.results?.length ?? 0} urgent maintenance request{(pendingMaintenance?.results?.length ?? 0) !== 1 ? 's' : ''}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Primary Metrics Cards */}
          <div className='grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'>
            {/* Total Properties */}
            <div className='rounded-lg border bg-card p-4 sm:p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div className='flex-1 min-w-0'>
                  <p className='text-sm font-medium text-muted-foreground truncate'>Total Properties</p>
                  <p className='text-2xl sm:text-3xl font-bold tabular-nums mt-1'>
                    {summary.total_properties}
                  </p>
                  <div className='mt-2 flex items-center gap-1'>
                    <Badge variant={summary.total_properties > 0 ? 'success' : 'default'} className='text-xs'>
                      {summary.total_properties > 0 ? 'Active' : 'No Properties'}
                    </Badge>
                  </div>
                </div>
                <div className='flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-lg bg-primary/10 ml-3 flex-shrink-0'>
                  <Home className='h-4 w-4 sm:h-5 sm:w-5 text-primary' />
                </div>
              </div>
            </div>

            {/* Occupancy Rate */}
            <div className='rounded-lg border bg-card p-4 sm:p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div className='flex-1 min-w-0'>
                  <p className='text-sm font-medium text-muted-foreground truncate'>Occupancy Rate</p>
                  <p className='text-2xl sm:text-3xl font-bold tabular-nums mt-1'>
                    {formatPercent(summary.average_occupancy)}
                  </p>
                  <div className='mt-2 flex items-center gap-1'>
                    {summary.average_occupancy >= 90 ? (
                      <TrendingUp className='h-3 w-3 text-green-600' />
                    ) : summary.average_occupancy >= 70 ? (
                      <Activity className='h-3 w-3 text-yellow-600' />
                    ) : (
                      <TrendingDown className='h-3 w-3 text-red-600' />
                    )}
                    <span className='text-xs text-muted-foreground'>
                      {summary.average_occupancy >= 90 ? 'Excellent' :
                       summary.average_occupancy >= 70 ? 'Good' : 'Needs Attention'}
                    </span>
                  </div>
                </div>
                <div className='flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-lg bg-primary/10 ml-3 flex-shrink-0'>
                  <BarChart3 className='h-4 w-4 sm:h-5 sm:w-5 text-primary' />
                </div>
              </div>
            </div>

            {/* Monthly Revenue */}
            <div className='rounded-lg border bg-card p-4 sm:p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div className='flex-1 min-w-0'>
                  <p className='text-sm font-medium text-muted-foreground truncate'>Monthly Revenue</p>
                  <p className='text-xl sm:text-2xl lg:text-3xl font-bold tabular-nums mt-1'>
                    {formatCurrency(summary.total_monthly_income)}
                  </p>
                  <div className='mt-2 flex items-center gap-1'>
                    <span className='text-xs text-muted-foreground'>
                      ${formatCurrency(summary.monthly_collections)} collected
                    </span>
                  </div>
                </div>
                <div className='flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-lg bg-primary/10 ml-3 flex-shrink-0'>
                  <DollarSign className='h-4 w-4 sm:h-5 sm:w-5 text-primary' />
                </div>
              </div>
            </div>

            {/* Active Leases */}
            <div className='rounded-lg border bg-card p-4 sm:p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div className='flex-1 min-w-0'>
                  <p className='text-sm font-medium text-muted-foreground truncate'>Active Leases</p>
                  <p className='text-2xl sm:text-3xl font-bold tabular-nums mt-1'>
                    {summary.active_leases}
                  </p>
                  <div className='mt-2 flex items-center gap-1'>
                    {summary.expiring_leases > 0 && (
                      <>
                        <Clock className='h-3 w-3 text-orange-600' />
                        <span className='text-xs text-orange-600'>
                          {summary.expiring_leases} expiring soon
                        </span>
                      </>
                    )}
                  </div>
                </div>
                <div className='flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-lg bg-primary/10 ml-3 flex-shrink-0'>
                  <Users className='h-4 w-4 sm:h-5 sm:w-5 text-primary' />
                </div>
              </div>
            </div>
          </div>

          {/* Secondary Metrics Cards */}
          <div className='grid gap-4 grid-cols-2 lg:grid-cols-4'>
            {/* Total Units */}
            <div className='rounded-lg border bg-card p-3 sm:p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div className='flex-1 min-w-0'>
                  <p className='text-xs sm:text-sm font-medium text-muted-foreground truncate'>Total Units</p>
                  <p className='text-lg sm:text-xl font-bold tabular-nums mt-1'>
                    {summary.total_units}
                  </p>
                  <div className='mt-1 text-xs text-muted-foreground'>
                    <span className='hidden sm:inline'>{summary.occupied_units} occupied • {summary.vacant_units} vacant</span>
                    <span className='sm:hidden'>{summary.occupied_units}/{summary.vacant_units}</span>
                  </div>
                </div>
                <div className='flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-lg bg-blue-100 ml-2 flex-shrink-0'>
                  <Building2 className='h-3 w-3 sm:h-4 sm:w-4 text-blue-600' />
                </div>
              </div>
            </div>

            {/* Outstanding Payments */}
            <div className='rounded-lg border bg-card p-3 sm:p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div className='flex-1 min-w-0'>
                  <p className='text-xs sm:text-sm font-medium text-muted-foreground truncate'>Outstanding</p>
                  <p className='text-base sm:text-lg font-bold tabular-nums mt-1'>
                    {formatCurrency(summary.total_outstanding)}
                  </p>
                  <div className='mt-1 flex items-center gap-1'>
                    {parseFloat(summary.total_outstanding) > 0 ? (
                      <AlertTriangle className='h-3 w-3 text-red-600 flex-shrink-0' />
                    ) : (
                      <CheckCircle className='h-3 w-3 text-green-600 flex-shrink-0' />
                    )}
                    <span className='text-xs text-muted-foreground truncate'>
                      {parseFloat(summary.total_outstanding) > 0 ? 'Needs attention' : 'All paid'}
                    </span>
                  </div>
                </div>
                <div className='flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-lg bg-red-100 ml-2 flex-shrink-0'>
                  <DollarSign className='h-3 w-3 sm:h-4 sm:w-4 text-red-600' />
                </div>
              </div>
            </div>

            {/* Maintenance Requests */}
            <div className='rounded-lg border bg-card p-3 sm:p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div className='flex-1 min-w-0'>
                  <p className='text-xs sm:text-sm font-medium text-muted-foreground truncate'>Maintenance</p>
                  <p className='text-lg sm:text-xl font-bold tabular-nums mt-1'>
                    {summary.open_maintenance}
                  </p>
                  <div className='mt-1 flex items-center gap-1'>
                    {summary.urgent_maintenance > 0 && (
                      <>
                        <AlertTriangle className='h-3 w-3 text-red-600 flex-shrink-0' />
                        <span className='text-xs text-red-600 truncate'>
                          {summary.urgent_maintenance} urgent
                        </span>
                      </>
                    )}
                  </div>
                </div>
                <div className='flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-lg bg-orange-100 ml-2 flex-shrink-0'>
                  <Wrench className='h-3 w-3 sm:h-4 sm:w-4 text-orange-600' />
                </div>
              </div>
            </div>

            {/* Net Profit */}
            <div className='rounded-lg border bg-card p-3 sm:p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div className='flex-1 min-w-0'>
                  <p className='text-xs sm:text-sm font-medium text-muted-foreground truncate'>Net Profit</p>
                  <p className={`text-base sm:text-lg font-bold tabular-nums mt-1 ${
                    accountingSummary && parseFloat(accountingSummary.summary.net_income) >= 0
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}>
                    {accountingSummary ? formatCurrency(accountingSummary.summary.net_income) : '$0.00'}
                  </p>
                  <div className='mt-1 text-xs text-muted-foreground truncate'>
                    This month
                  </div>
                </div>
                <div className={`flex h-6 w-6 sm:h-8 sm:w-8 items-center justify-center rounded-lg ml-2 flex-shrink-0 ${
                  accountingSummary && parseFloat(accountingSummary.summary.net_income) >= 0
                    ? 'bg-green-100'
                    : 'bg-red-100'
                }`}>
                  {accountingSummary && parseFloat(accountingSummary.summary.net_income) >= 0 ? (
                    <TrendingUp className='h-3 w-3 sm:h-4 sm:w-4 text-green-600' />
                  ) : (
                    <TrendingDown className='h-3 w-3 sm:h-4 sm:w-4 text-red-600' />
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Charts Section */}
          <div className='grid gap-6 grid-cols-1 xl:grid-cols-2'>
            {/* Revenue Chart */}
            <div className='rounded-lg border bg-card p-4 sm:p-6 shadow-sm'>
              <div className='mb-4'>
                <h3 className='text-base sm:text-lg font-semibold'>Revenue Overview</h3>
                <p className='text-xs sm:text-sm text-muted-foreground'>
                  Monthly revenue and collections for the past year
                </p>
              </div>
              <div className='h-64 sm:h-80'>
                <ChartAreaInteractive
                  data={charts.monthly_revenue.map(item => ({
                    month: item.month,
                    revenue: item.revenue,
                    collections: item.collections,
                  }))}
                />
              </div>
            </div>

            {/* Financial Summary */}
            <div className='rounded-lg border bg-card p-4 sm:p-6 shadow-sm'>
              <div className='mb-4'>
                <h3 className='text-base sm:text-lg font-semibold'>Financial Summary</h3>
                <p className='text-xs sm:text-sm text-muted-foreground'>
                  Income and expense breakdown for this month
                </p>
              </div>
              <div className='space-y-4'>
                <div className='flex items-center justify-between'>
                  <div>
                    <p className='text-sm font-medium text-muted-foreground'>Total Income</p>
                    <p className='text-lg font-semibold text-green-600'>
                      {accountingSummary ? formatCurrency(accountingSummary.summary.total_income) : '$0.00'}
                    </p>
                  </div>
                  <TrendingUp className='h-5 w-5 text-green-600' />
                </div>

                <div className='flex items-center justify-between'>
                  <div>
                    <p className='text-sm font-medium text-muted-foreground'>Total Expenses</p>
                    <p className='text-lg font-semibold text-red-600'>
                      {accountingSummary ? formatCurrency(accountingSummary.summary.total_expenses) : '$0.00'}
                    </p>
                  </div>
                  <TrendingDown className='h-5 w-5 text-red-600' />
                </div>

                <div className='pt-2 border-t'>
                  <div className='flex items-center justify-between'>
                    <p className='text-sm font-medium'>Net Profit</p>
                    <p className={`text-lg font-bold ${
                      accountingSummary && parseFloat(accountingSummary.summary.net_income) >= 0
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}>
                      {accountingSummary ? formatCurrency(accountingSummary.summary.net_income) : '$0.00'}
                    </p>
                  </div>
                </div>

                <div className='text-xs text-muted-foreground'>
                  {accountingSummary?.summary.transaction_count || 0} transactions this month
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          {data.recent_activity && data.recent_activity.length > 0 && (
            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='mb-4'>
                <h3 className='text-lg font-semibold'>Recent Activity</h3>
                <p className='text-sm text-muted-foreground'>
                  Latest payments and maintenance activities
                </p>
              </div>
              <div className='space-y-3'>
                {data.recent_activity.slice(0, 5).map((activity, index) => (
                  <div key={index} className='flex items-start gap-3 p-3 rounded-lg bg-muted/50'>
                    <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                      activity.type === 'payment' ? 'bg-green-100' : 'bg-orange-100'
                    }`}>
                      {activity.type === 'payment' ? (
                        <DollarSign className='h-4 w-4 text-green-600' />
                      ) : (
                        <Wrench className='h-4 w-4 text-orange-600' />
                      )}
                    </div>
                    <div className='flex-1 min-w-0'>
                      <p className='text-sm font-medium truncate'>{activity.description}</p>
                      <div className='flex items-center gap-2 mt-1'>
                        <span className='text-xs text-muted-foreground'>
                          {new Date(activity.date).toLocaleDateString()}
                        </span>
                        {activity.amount && (
                          <span className='text-xs font-medium text-green-600'>
                            {activity.amount}
                          </span>
                        )}
                        {activity.priority && (
                          <Badge variant={
                            activity.priority === 'urgent' ? 'danger' :
                            activity.priority === 'high' ? 'warning' : 'default'
                          } className='text-xs'>
                            {activity.priority}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Property Portfolio & Quick Actions */}
          <div className='grid gap-6 md:grid-cols-3'>
            {/* Property Types Overview */}
            <div className='md:col-span-2 rounded-lg border bg-card p-6 shadow-sm'>
              <div className='mb-4'>
                <h3 className='text-lg font-semibold'>Property Portfolio</h3>
                <p className='text-sm text-muted-foreground'>
                  Distribution of your properties by type
                </p>
              </div>
              <div className='space-y-4'>
                {Object.entries(charts.property_types).map(([type, data]) => {
                  const occupancyRate = data.total_units > 0 ? (data.occupied_units / data.total_units) * 100 : 0
                  return (
                    <div key={type} className='flex items-center justify-between p-4 rounded-lg border'>
                      <div className='flex-1'>
                        <div className='flex items-center gap-3'>
                          <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                            <Home className='h-5 w-5 text-primary' />
                          </div>
                          <div>
                            <p className='font-medium'>{type}</p>
                            <p className='text-sm text-muted-foreground'>
                              {data.count} propert{data.count !== 1 ? 'ies' : 'y'} • {data.total_units} units
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className='text-right'>
                        <p className='font-medium'>{formatPercent(occupancyRate)}</p>
                        <p className='text-sm text-muted-foreground'>
                          ${data.monthly_income.toLocaleString()}/mo
                        </p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Quick Actions */}
            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='mb-4'>
                <h3 className='text-lg font-semibold'>Quick Actions</h3>
                <p className='text-sm text-muted-foreground'>
                  Common tasks and shortcuts
                </p>
              </div>
              <div className='space-y-3'>
                <a
                  href='/properties'
                  className='flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors'
                >
                  <div className='flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100'>
                    <Home className='h-4 w-4 text-blue-600' />
                  </div>
                  <div>
                    <p className='font-medium text-sm'>Add Property</p>
                    <p className='text-xs text-muted-foreground'>Expand your portfolio</p>
                  </div>
                </a>

                <a
                  href='/tenants'
                  className='flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors'
                >
                  <div className='flex h-8 w-8 items-center justify-center rounded-lg bg-green-100'>
                    <Users className='h-4 w-4 text-green-600' />
                  </div>
                  <div>
                    <p className='font-medium text-sm'>Add Tenant</p>
                    <p className='text-xs text-muted-foreground'>Onboard new residents</p>
                  </div>
                </a>

                <a
                  href='/payments'
                  className='flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors'
                >
                  <div className='flex h-8 w-8 items-center justify-center rounded-lg bg-yellow-100'>
                    <DollarSign className='h-4 w-4 text-yellow-600' />
                  </div>
                  <div>
                    <p className='font-medium text-sm'>View Payments</p>
                    <p className='text-xs text-muted-foreground'>Check outstanding balances</p>
                  </div>
                </a>

                <a
                  href='/maintenance'
                  className='flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors'
                >
                  <div className='flex h-8 w-8 items-center justify-center rounded-lg bg-orange-100'>
                    <Wrench className='h-4 w-4 text-orange-600' />
                  </div>
                  <div>
                    <p className='font-medium text-sm'>Report Issue</p>
                    <p className='text-xs text-muted-foreground'>Maintenance requests</p>
                  </div>
                </a>
              </div>
            </div>
          </div>

          {/* Performance Indicators */}
          <div className='rounded-lg border bg-card p-6 shadow-sm'>
            <div className='mb-4'>
              <h3 className='text-lg font-semibold'>Performance Indicators</h3>
              <p className='text-sm text-muted-foreground'>
                Key metrics and trends for your property management business
              </p>
            </div>
            <div className='grid gap-4 md:grid-cols-3'>
              <div className='text-center p-4 rounded-lg bg-muted/50'>
                <div className='text-2xl font-bold text-primary mb-1'>
                  {formatPercent(summary.average_occupancy)}
                </div>
                <p className='text-sm text-muted-foreground'>Average Occupancy Rate</p>
                <div className='mt-2 text-xs'>
                  {summary.average_occupancy >= 90 ? '🏆 Excellent performance' :
                   summary.average_occupancy >= 80 ? '✅ Good performance' :
                   '⚠️ Needs improvement'}
                </div>
              </div>

              <div className='text-center p-4 rounded-lg bg-muted/50'>
                <div className='text-2xl font-bold text-green-600 mb-1'>
                  {summary.active_leases}
                </div>
                <p className='text-sm text-muted-foreground'>Active Leases</p>
                <div className='mt-2 text-xs'>
                  {summary.expiring_leases > 0 ?
                    `⚠️ ${summary.expiring_leases} expiring soon` :
                    '✅ All leases current'}
                </div>
              </div>

              <div className='text-center p-4 rounded-lg bg-muted/50'>
                <div className='text-2xl font-bold text-blue-600 mb-1'>
                  {summary.total_properties}
                </div>
                <p className='text-sm text-muted-foreground'>Properties Managed</p>
                <div className='mt-2 text-xs'>
                  {summary.total_properties > 5 ? '🏢 Large portfolio' :
                   summary.total_properties > 2 ? '🏠 Growing portfolio' :
                   '🌱 Starting out'}
                </div>
              </div>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default DashboardPage
