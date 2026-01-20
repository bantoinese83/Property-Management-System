import React from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { useAuth } from '../hooks/useAuth'
import { Card } from '../components/common/Card'
import { Button } from '../components/common/Button'
import { ErrorMessage, SkeletonCard, Skeleton } from '../components/common'
import '../styles/pages/DashboardPage.css'

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

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth()
  const { data, loading, error, refetch } = useApi<DashboardAnalytics>(
    `${API_ENDPOINTS.PROPERTIES.LIST}dashboard_analytics/`
  )

  if (loading) {
    return (
      <div className='dashboard-page'>
        <div className='dashboard-header'>
          <div>
            <Skeleton height={32} width={200} className='mb-2' />
            <Skeleton height={20} width={300} />
          </div>
        </div>

        <div className='dashboard-metrics'>
          <div className='metrics-grid'>
            {Array.from({ length: 4 }).map((_, index) => (
              <SkeletonCard key={index} />
            ))}
          </div>
        </div>

        <div className='dashboard-content'>
          <div className='dashboard-charts'>
            <div className='chart-container'>
              <Skeleton height={300} variant='rounded' className='mb-4' />
            </div>
          </div>

          <div className='dashboard-activity'>
            <SkeletonCard />
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className='flex h-[80vh] items-center justify-center'>
        <ErrorMessage message={error.message} title='Failed to load dashboard' />
      </div>
    )
  }

  if (!data) {
    return (
      <div className='flex h-[80vh] items-center justify-center'>
        <ErrorMessage
          message='No analytics data was returned from the server.'
          title='No Data Available'
        />
      </div>
    )
  }

  const { summary, charts, recent_activity } = data

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
    <div className='dashboard-page'>
      <div className='dashboard-header'>
        <div>
          <h1>Property Management Dashboard</h1>
          <p>Welcome back, {user?.username}! Here's an overview of your property portfolio.</p>
        </div>
        <div className='header-actions'>
          <Button variant='ghost' onClick={() => refetch()}>
            Refresh
          </Button>
          <Button variant='secondary' onClick={logout}>
            Logout
          </Button>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className='metrics-grid'>
        <Card className='metric-card'>
          <div className='metric-value'>{summary.total_properties}</div>
          <div className='metric-label'>Total Properties</div>
          <div className='metric-icon'>🏠</div>
        </Card>

        <Card className='metric-card'>
          <div className='metric-value'>{summary.total_units}</div>
          <div className='metric-label'>Total Units</div>
          <div className='metric-icon'>🏢</div>
        </Card>

        <Card className='metric-card'>
          <div className='metric-value'>{formatPercent(summary.average_occupancy)}</div>
          <div className='metric-label'>Average Occupancy</div>
          <div className='metric-icon'>📊</div>
        </Card>

        <Card className='metric-card'>
          <div className='metric-value'>{formatCurrency(summary.total_monthly_income)}</div>
          <div className='metric-label'>Monthly Income</div>
          <div className='metric-icon'>💰</div>
        </Card>

        <Card className='metric-card'>
          <div className='metric-value'>{summary.active_leases}</div>
          <div className='metric-label'>Active Leases</div>
          <div className='metric-icon'>📄</div>
        </Card>

        <Card className='metric-card'>
          <div className='metric-value'>{summary.open_maintenance}</div>
          <div className='metric-label'>Open Maintenance</div>
          <div className='metric-icon'>🔧</div>
        </Card>
      </div>

      {/* Financial Overview */}
      <div className='dashboard-section'>
        <h2>Financial Overview</h2>
        <div className='financial-grid'>
          <Card className='financial-card'>
            <h3>Monthly Collections</h3>
            <div className='financial-amount'>{formatCurrency(summary.monthly_collections)}</div>
            <p>Last 30 days</p>
          </Card>

          <Card className='financial-card'>
            <h3>Outstanding Payments</h3>
            <div className='financial-amount outstanding'>
              {formatCurrency(summary.total_outstanding)}
            </div>
            <p>Pending collection</p>
          </Card>

          <Card className='financial-card'>
            <h3>Annual Income</h3>
            <div className='financial-amount'>{formatCurrency(summary.total_annual_income)}</div>
            <p>Projected yearly total</p>
          </Card>

          <Card className='financial-card'>
            <h3>Occupancy Details</h3>
            <div className='occupancy-details'>
              <div className='occupancy-item'>
                <span className='occupancy-label'>Occupied:</span>
                <span className='occupancy-value'>{summary.occupied_units}</span>
              </div>
              <div className='occupancy-item'>
                <span className='occupancy-label'>Vacant:</span>
                <span className='occupancy-value'>{summary.vacant_units}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Charts and Analytics */}
      <div className='dashboard-section'>
        <h2>Property Portfolio</h2>
        <div className='portfolio-grid'>
          <Card className='portfolio-card'>
            <h3>Property Types Distribution</h3>
            <div className='property-types'>
              {Object.entries(charts.property_types).map(([type, data]) => (
                <div key={type} className='property-type-item'>
                  <div className='property-type-header'>
                    <span className='property-type-name'>{type}</span>
                    <span className='property-type-count'>{data.count} properties</span>
                  </div>
                  <div className='property-type-stats'>
                    <span>{data.total_units} units</span>
                    <span>{formatCurrency(data.monthly_income.toString())}/mo</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className='portfolio-card'>
            <h3>Monthly Revenue Trend</h3>
            <div className='revenue-chart'>
              {charts.monthly_revenue.map(month => (
                <div key={month.month} className='revenue-bar'>
                  <div className='revenue-label'>{month.month}</div>
                  <div
                    className='revenue-fill'
                    style={{
                      height: `${Math.max((month.revenue / 10000) * 100, 10)}px`,
                    }}
                    title={`$${month.revenue.toLocaleString()}`}
                  ></div>
                  <div className='revenue-value'>${month.revenue.toLocaleString()}</div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Alerts and Notifications */}
      {(summary.expiring_leases > 0 || summary.urgent_maintenance > 0) && (
        <div className='dashboard-section'>
          <h2>Alerts</h2>
          <div className='alerts-grid'>
            {summary.expiring_leases > 0 && (
              <Card className='alert-card warning'>
                <div className='alert-icon'>⚠️</div>
                <div className='alert-content'>
                  <h4>Expiring Leases</h4>
                  <p>{summary.expiring_leases} lease(s) expiring within 30 days</p>
                </div>
              </Card>
            )}

            {summary.urgent_maintenance > 0 && (
              <Card className='alert-card urgent'>
                <div className='alert-icon'>🚨</div>
                <div className='alert-content'>
                  <h4>Urgent Maintenance</h4>
                  <p>{summary.urgent_maintenance} urgent maintenance request(s)</p>
                </div>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className='dashboard-section'>
        <h2>Recent Activity</h2>
        <Card className='activity-card'>
          <div className='activity-list'>
            {recent_activity.length === 0 ? (
              <p className='no-activity'>No recent activity</p>
            ) : (
              recent_activity.map((activity, index) => (
                <div key={index} className={`activity-item ${activity.type}`}>
                  <div className='activity-icon'>{activity.type === 'payment' ? '💰' : '🔧'}</div>
                  <div className='activity-content'>
                    <div className='activity-description'>{activity.description}</div>
                    <div className='activity-meta'>
                      <span className='activity-property'>{activity.property}</span>
                      <span className='activity-date'>
                        {new Date(activity.date).toLocaleDateString()}
                      </span>
                      {activity.amount && (
                        <span className='activity-amount'>{formatCurrency(activity.amount)}</span>
                      )}
                      {activity.priority && (
                        <span className={`activity-priority ${activity.priority}`}>
                          {activity.priority}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}

export default DashboardPage
