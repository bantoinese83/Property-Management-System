import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/common/Input'
import { LoadingSpinner, ErrorMessage, Badge } from '../components/common'
import {
  Shield,
  Search,
  Download,
  User,
  Activity,
  AlertTriangle,
  Eye,
  EyeOff,
  Calendar,
} from 'lucide-react'

interface AuditLog {
  id: number
  username: string
  action: string
  action_description: string
  content_type_name: string
  app_label: string
  model_name: string
  timestamp: string
  ip_address?: string
  changed_fields: string[]
  is_sensitive: boolean
}

interface AuditResponse {
  results: AuditLog[]
  count: number
  next?: string
  previous?: string
}

const AuditPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [actionFilter, setActionFilter] = useState('')
  const [dateFilter, setDateFilter] = useState('')
  const [showSensitive, setShowSensitive] = useState(false)

  const { data, loading, error } = useApi<AuditResponse>(
    `${API_ENDPOINTS.AUDIT}?search=${searchTerm}&action=${actionFilter}&timestamp__date=${dateFilter}`
  )

  const logs = data?.results || []

  const getActionColor = (action: string) => {
    switch (action) {
      case 'create':
        return 'bg-green-100 text-green-800'
      case 'update':
        return 'bg-blue-100 text-blue-800'
      case 'delete':
        return 'bg-red-100 text-red-800'
      case 'login':
        return 'bg-purple-100 text-purple-800'
      case 'logout':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'create':
        return <Activity className='h-4 w-4' />
      case 'update':
        return <Activity className='h-4 w-4' />
      case 'delete':
        return <AlertTriangle className='h-4 w-4' />
      case 'login':
        return <User className='h-4 w-4' />
      case 'logout':
        return <User className='h-4 w-4' />
      default:
        return <Activity className='h-4 w-4' />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString()
  }

  const filteredLogs = showSensitive ? logs : logs.filter(log => !log.is_sensitive)

  if (loading && !logs.length) {
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
            <LoadingSpinner size='lg' />
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
            <ErrorMessage message={error.message} title='Failed to load audit logs' />
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
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
          {/* Header */}
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold tracking-tight'>Audit Trail</h1>
              <p className='text-muted-foreground'>
                Track and monitor all system activities and changes
              </p>
            </div>
            <div className='flex gap-2'>
              <Button variant='outline' onClick={() => setShowSensitive(!showSensitive)}>
                {showSensitive ? (
                  <EyeOff className='h-4 w-4 mr-2' />
                ) : (
                  <Eye className='h-4 w-4 mr-2' />
                )}
                {showSensitive ? 'Hide Sensitive' : 'Show Sensitive'}
              </Button>
              <Button variant='outline'>
                <Download className='h-4 w-4 mr-2' />
                Export Logs
              </Button>
            </div>
          </div>

          {/* Filters */}
          <Card>
            <CardContent className='pt-6'>
              <div className='flex flex-col gap-4 md:flex-row md:items-end'>
                <div className='flex-1'>
                  <label className='text-sm font-medium mb-2 block'>Search</label>
                  <div className='relative'>
                    <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground' />
                    <Input
                      placeholder='Search by username, action, or description...'
                      value={searchTerm}
                      onChange={e => setSearchTerm(e.target.value)}
                      className='pl-10'
                    />
                  </div>
                </div>

                <div className='w-full md:w-48'>
                  <label className='text-sm font-medium mb-2 block'>Action</label>
                  <select
                    value={actionFilter}
                    onChange={e => setActionFilter(e.target.value)}
                    className='flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
                  >
                    <option value=''>All Actions</option>
                    <option value='create'>Create</option>
                    <option value='update'>Update</option>
                    <option value='delete'>Delete</option>
                    <option value='login'>Login</option>
                    <option value='logout'>Logout</option>
                  </select>
                </div>

                <div className='w-full md:w-48'>
                  <label className='text-sm font-medium mb-2 block'>Date</label>
                  <Input
                    type='date'
                    value={dateFilter}
                    onChange={e => setDateFilter(e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stats */}
          <div className='grid gap-4 md:grid-cols-4'>
            <Card>
              <CardContent className='pt-6'>
                <div className='flex items-center justify-between'>
                  <div>
                    <p className='text-sm font-medium text-muted-foreground'>Total Logs</p>
                    <p className='text-2xl font-bold'>{filteredLogs.length}</p>
                  </div>
                  <Shield className='h-8 w-8 text-muted-foreground' />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className='pt-6'>
                <div className='flex items-center justify-between'>
                  <div>
                    <p className='text-sm font-medium text-muted-foreground'>Today</p>
                    <p className='text-2xl font-bold'>
                      {
                        filteredLogs.filter(
                          log =>
                            new Date(log.timestamp).toDateString() === new Date().toDateString()
                        ).length
                      }
                    </p>
                  </div>
                  <Calendar className='h-8 w-8 text-muted-foreground' />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className='pt-6'>
                <div className='flex items-center justify-between'>
                  <div>
                    <p className='text-sm font-medium text-muted-foreground'>Sensitive Actions</p>
                    <p className='text-2xl font-bold'>
                      {logs.filter(log => log.is_sensitive).length}
                    </p>
                  </div>
                  <AlertTriangle className='h-8 w-8 text-muted-foreground' />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className='pt-6'>
                <div className='flex items-center justify-between'>
                  <div>
                    <p className='text-sm font-medium text-muted-foreground'>Active Users</p>
                    <p className='text-2xl font-bold'>
                      {new Set(filteredLogs.map(log => log.username)).size}
                    </p>
                  </div>
                  <User className='h-8 w-8 text-muted-foreground' />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Audit Logs */}
          <Card>
            <CardHeader>
              <CardTitle>Activity Log</CardTitle>
              <CardDescription>
                Complete history of system activities and user actions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {filteredLogs.length > 0 ? (
                <div className='space-y-4'>
                  {filteredLogs.map(log => (
                    <div
                      key={log.id}
                      className={`flex items-start gap-4 p-4 rounded-lg border ${
                        log.is_sensitive ? 'bg-red-50 border-red-200' : 'bg-muted/50'
                      }`}
                    >
                      <div className={`p-2 rounded-full ${getActionColor(log.action)}`}>
                        {getActionIcon(log.action)}
                      </div>

                      <div className='flex-1 min-w-0'>
                        <div className='flex items-center gap-2 mb-2'>
                          <span className='font-medium'>{log.username}</span>
                          <Badge variant='outline' className={getActionColor(log.action)}>
                            {log.action}
                          </Badge>
                          {log.is_sensitive && (
                            <Badge variant='destructive' className='text-xs'>
                              Sensitive
                            </Badge>
                          )}
                        </div>

                        <p className='text-sm text-muted-foreground mb-2'>
                          {log.action_description}
                        </p>

                        <div className='flex items-center gap-4 text-xs text-muted-foreground'>
                          <span>{formatTimestamp(log.timestamp)}</span>
                          <span>
                            {log.app_label}.{log.model_name}
                          </span>
                          {log.ip_address && <span>IP: {log.ip_address}</span>}
                          {log.changed_fields.length > 0 && (
                            <span>Changed: {log.changed_fields.join(', ')}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className='text-center py-8'>
                  <Shield className='h-12 w-12 text-muted-foreground mx-auto mb-4' />
                  <h3 className='text-lg font-medium mb-2'>No audit logs found</h3>
                  <p className='text-sm text-muted-foreground'>
                    {showSensitive
                      ? 'No logs match your current filters.'
                      : 'No logs available or sensitive logs are hidden.'}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default AuditPage
