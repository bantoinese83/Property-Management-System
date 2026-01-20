import React from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { AppSidebar } from '../components/app-sidebar'
import { ChartAreaInteractive } from '../components/chart-area-interactive'
import { DataTable } from '../components/data-table'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { ErrorMessage } from '../components/common'
import { Home, Building2, BarChart3, DollarSign } from 'lucide-react'

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

  if (loading) {
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
            {/* Loading skeleton for metrics cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="h-32 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>

            {/* Loading skeleton for chart */}
            <div className="h-96 rounded-lg bg-muted animate-pulse" />

            {/* Loading skeleton for table */}
            <div className="h-64 rounded-lg bg-muted animate-pulse" />
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
          <div className="flex flex-1 items-center justify-center p-4 lg:p-6">
            <ErrorMessage message={error.message} title='Failed to load dashboard' />
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
  }

  if (!data) {
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
          <div className="flex flex-1 items-center justify-center p-4 lg:p-6">
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
      style={{
        "--sidebar-width": "280px",
        "--header-height": "60px",
      } as React.CSSProperties}
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
          {/* Metrics Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {/* Total Properties */}
            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Properties</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl">
                    {summary.total_properties}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Home className="h-5 w-5 text-primary" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-sm text-muted-foreground">Property portfolio</span>
              </div>
            </div>

            {/* Total Units */}
            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Units</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl">
                    {summary.total_units}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Building2 className="h-5 w-5 text-primary" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-sm text-muted-foreground">Available units</span>
              </div>
            </div>

            {/* Average Occupancy */}
            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Average Occupancy</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl">
                    {formatPercent(summary.average_occupancy)}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <BarChart3 className="h-5 w-5 text-primary" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-sm text-muted-foreground">Occupancy rate</span>
              </div>
            </div>

            {/* Monthly Income */}
            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Monthly Income</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl">
                    {formatCurrency(summary.total_monthly_income)}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <DollarSign className="h-5 w-5 text-primary" />
                </div>
              </div>
              <div className="mt-4">
                <span className="text-sm text-muted-foreground">Monthly revenue</span>
              </div>
            </div>
          </div>

          {/* Chart Section */}
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <div className="mb-4">
              <h3 className="text-lg font-semibold">Revenue Overview</h3>
              <p className="text-sm text-muted-foreground">
                Monthly revenue and collections for the past year
              </p>
            </div>
            <ChartAreaInteractive
              data={charts.monthly_revenue.map(item => ({
                month: item.month,
                revenue: item.revenue,
                collections: item.collections
              }))}
            />
          </div>

          {/* Property Types Table */}
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <div className="mb-4">
              <h3 className="text-lg font-semibold">Property Types</h3>
              <p className="text-sm text-muted-foreground">
                Overview of your property portfolio by type
              </p>
            </div>
            <DataTable
              data={Object.entries(charts.property_types).map(([type, data], index) => ({
                id: index + 1,
                header: type,
                type: "Property Type",
                status: "Active",
                target: data.total_units.toString(),
                limit: data.occupied_units.toString(),
                reviewer: `${data.count} properties`
              }))}
            />
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default DashboardPage
