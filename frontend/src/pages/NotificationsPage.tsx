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
import {
  Bell,
  BellRing,
  Settings,
  CheckCircle,
  Archive,
  MoreVertical,
  Info,
  Home,
  Users,
  FileText,
  DollarSign,
  Wrench,
} from 'lucide-react'

interface Notification {
  id: number
  notification_type: string
  title: string
  message: string
  priority: string
  is_read: boolean
  is_archived: boolean
  action_url?: string
  created_at: string
  time_ago: string
}

interface NotificationPreferences {
  email_enabled: boolean
  email_payment_reminders: boolean
  email_maintenance_updates: boolean
  email_lease_updates: boolean
  email_system_updates: boolean
  in_app_enabled: boolean
  in_app_payment_reminders: boolean
  in_app_maintenance_updates: boolean
  in_app_lease_updates: boolean
  in_app_system_updates: boolean
  push_enabled: boolean
  push_payment_reminders: boolean
  push_maintenance_updates: boolean
  push_lease_updates: boolean
  push_system_updates: boolean
  digest_frequency: string
}

const NotificationsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'notifications' | 'preferences'>('notifications')

  const {
    data: notificationsData,
    loading: notificationsLoading,
    refetch: refetchNotifications,
  } = useApi<{
    results: Notification[]
    count: number
  }>(`${API_ENDPOINTS.NOTIFICATIONS.LIST}?page_size=50`)

  const { data: preferencesData, loading: preferencesLoading } = useApi<NotificationPreferences>(
    API_ENDPOINTS.NOTIFICATION_PREFERENCES
  )

  const { data: unreadCountData } = useApi<{ unread_count: number }>(
    API_ENDPOINTS.NOTIFICATIONS.UNREAD_COUNT
  )

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'system':
        return <Info className='h-4 w-4' />
      case 'payment':
        return <DollarSign className='h-4 w-4' />
      case 'maintenance':
        return <Wrench className='h-4 w-4' />
      case 'lease':
        return <FileText className='h-4 w-4' />
      case 'tenant':
        return <Users className='h-4 w-4' />
      case 'property':
        return <Home className='h-4 w-4' />
      default:
        return <Bell className='h-4 w-4' />
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800'
      case 'high':
        return 'bg-orange-100 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const markAsRead = async (notificationId: number) => {
    try {
      await fetch(API_ENDPOINTS.NOTIFICATIONS.MARK_READ(notificationId), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      refetchNotifications()
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }

  const archiveNotification = async (notificationId: number) => {
    try {
      await fetch(API_ENDPOINTS.NOTIFICATIONS.ARCHIVE(notificationId), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      refetchNotifications()
    } catch (error) {
      console.error('Error archiving notification:', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      await fetch(API_ENDPOINTS.NOTIFICATIONS.MARK_ALL_READ, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      refetchNotifications()
    } catch (error) {
      console.error('Error marking all notifications as read:', error)
    }
  }

  const updatePreferences = async (preferences: Partial<NotificationPreferences>) => {
    try {
      await fetch(API_ENDPOINTS.NOTIFICATION_PREFERENCES, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(preferences),
      })
    } catch (error) {
      console.error('Error updating preferences:', error)
    }
  }

  const notifications = notificationsData?.results || []
  const unreadCount = unreadCountData?.unread_count || 0

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
              <h1 className='text-3xl font-bold tracking-tight'>Notifications</h1>
              <p className='text-muted-foreground'>Manage your notifications and preferences</p>
            </div>
            {unreadCount > 0 && (
              <Badge className='bg-red-100 text-red-800'>{unreadCount} unread</Badge>
            )}
          </div>

          {/* Tabs */}
          <div className='flex space-x-1 bg-muted p-1 rounded-lg w-fit'>
            <button
              onClick={() => setActiveTab('notifications')}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors flex items-center gap-2 ${
                activeTab === 'notifications'
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Bell className='h-4 w-4' />
              Notifications
              {unreadCount > 0 && (
                <span className='bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full'>
                  {unreadCount}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('preferences')}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors flex items-center gap-2 ${
                activeTab === 'preferences'
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Settings className='h-4 w-4' />
              Preferences
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'notifications' && (
            <div className='space-y-4'>
              {/* Actions */}
              <div className='flex items-center justify-between'>
                <div className='flex gap-2'>
                  <Button
                    variant='outline'
                    size='sm'
                    onClick={markAllAsRead}
                    disabled={unreadCount === 0}
                  >
                    <CheckCircle className='h-4 w-4 mr-2' />
                    Mark All as Read
                  </Button>
                </div>
                <div className='text-sm text-muted-foreground'>
                  {notifications.length} notification{notifications.length !== 1 ? 's' : ''}
                </div>
              </div>

              {/* Notifications List */}
              {notificationsLoading ? (
                <div className='flex justify-center py-8'>
                  <LoadingSpinner size='lg' />
                </div>
              ) : notifications.length > 0 ? (
                <div className='space-y-2'>
                  {notifications.map(notification => (
                    <Card
                      key={notification.id}
                      className={`transition-colors ${
                        !notification.is_read ? 'bg-blue-50/50 border-blue-200' : ''
                      }`}
                    >
                      <CardContent className='p-4'>
                        <div className='flex items-start justify-between'>
                          <div className='flex items-start gap-3 flex-1'>
                            <div
                              className={`p-2 rounded-full ${
                                notification.priority === 'urgent'
                                  ? 'bg-red-100'
                                  : notification.priority === 'high'
                                    ? 'bg-orange-100'
                                    : 'bg-blue-100'
                              }`}
                            >
                              {getNotificationIcon(notification.notification_type)}
                            </div>

                            <div className='flex-1 min-w-0'>
                              <div className='flex items-center gap-2 mb-1'>
                                <h3 className='font-medium text-sm truncate'>
                                  {notification.title}
                                </h3>
                                <Badge
                                  className={getPriorityColor(notification.priority)}
                                  variant='outline'
                                >
                                  {notification.priority}
                                </Badge>
                                {!notification.is_read && (
                                  <div className='h-2 w-2 bg-blue-500 rounded-full' />
                                )}
                              </div>

                              <p className='text-sm text-muted-foreground mb-2'>
                                {notification.message}
                              </p>

                              <div className='flex items-center justify-between'>
                                <span className='text-xs text-muted-foreground'>
                                  {notification.time_ago}
                                </span>

                                <div className='flex items-center gap-1'>
                                  {!notification.is_read && (
                                    <Button
                                      variant='ghost'
                                      size='sm'
                                      onClick={() => markAsRead(notification.id)}
                                      className='h-8 px-2'
                                    >
                                      <CheckCircle className='h-3 w-3' />
                                    </Button>
                                  )}

                                  {!notification.is_archived && (
                                    <Button
                                      variant='ghost'
                                      size='sm'
                                      onClick={() => archiveNotification(notification.id)}
                                      className='h-8 px-2'
                                    >
                                      <Archive className='h-3 w-3' />
                                    </Button>
                                  )}

                                  <Button variant='ghost' size='sm' className='h-8 px-2'>
                                    <MoreVertical className='h-3 w-3' />
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card>
                  <CardContent className='flex flex-col items-center justify-center py-12'>
                    <Bell className='h-12 w-12 text-muted-foreground mb-4' />
                    <h3 className='text-lg font-medium mb-2'>No notifications</h3>
                    <p className='text-sm text-muted-foreground text-center max-w-sm'>
                      When you have notifications, they'll appear here. You can customize your
                      notification preferences in the settings tab.
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {activeTab === 'preferences' && (
            <div className='grid gap-6 md:grid-cols-2'>
              {/* Email Preferences */}
              <Card>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2'>
                    <BellRing className='h-5 w-5' />
                    Email Notifications
                  </CardTitle>
                  <CardDescription>
                    Choose which notifications you want to receive via email
                  </CardDescription>
                </CardHeader>
                <CardContent className='space-y-4'>
                  {preferencesLoading ? (
                    <LoadingSpinner size='sm' />
                  ) : (
                    <>
                      <div className='flex items-center justify-between'>
                        <div>
                          <label className='text-sm font-medium'>Enable Email Notifications</label>
                          <p className='text-xs text-muted-foreground'>
                            Receive notifications via email
                          </p>
                        </div>
                        <input
                          type='checkbox'
                          checked={preferencesData?.email_enabled || false}
                          onChange={e => updatePreferences({ email_enabled: e.target.checked })}
                          className='rounded border-gray-300'
                        />
                      </div>

                      <div className='space-y-3 pl-4 border-l-2 border-muted'>
                        <div className='flex items-center justify-between'>
                          <span className='text-sm'>Payment Reminders</span>
                          <input
                            type='checkbox'
                            checked={preferencesData?.email_payment_reminders || false}
                            onChange={e =>
                              updatePreferences({ email_payment_reminders: e.target.checked })
                            }
                            disabled={!preferencesData?.email_enabled}
                            className='rounded border-gray-300'
                          />
                        </div>

                        <div className='flex items-center justify-between'>
                          <span className='text-sm'>Maintenance Updates</span>
                          <input
                            type='checkbox'
                            checked={preferencesData?.email_maintenance_updates || false}
                            onChange={e =>
                              updatePreferences({ email_maintenance_updates: e.target.checked })
                            }
                            disabled={!preferencesData?.email_enabled}
                            className='rounded border-gray-300'
                          />
                        </div>

                        <div className='flex items-center justify-between'>
                          <span className='text-sm'>Lease Updates</span>
                          <input
                            type='checkbox'
                            checked={preferencesData?.email_lease_updates || false}
                            onChange={e =>
                              updatePreferences({ email_lease_updates: e.target.checked })
                            }
                            disabled={!preferencesData?.email_enabled}
                            className='rounded border-gray-300'
                          />
                        </div>

                        <div className='flex items-center justify-between'>
                          <span className='text-sm'>System Updates</span>
                          <input
                            type='checkbox'
                            checked={preferencesData?.email_system_updates || false}
                            onChange={e =>
                              updatePreferences({ email_system_updates: e.target.checked })
                            }
                            disabled={!preferencesData?.email_enabled}
                            className='rounded border-gray-300'
                          />
                        </div>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>

              {/* In-App Preferences */}
              <Card>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2'>
                    <Bell className='h-5 w-5' />
                    In-App Notifications
                  </CardTitle>
                  <CardDescription>
                    Choose which notifications you want to see in the app
                  </CardDescription>
                </CardHeader>
                <CardContent className='space-y-4'>
                  {preferencesLoading ? (
                    <LoadingSpinner size='sm' />
                  ) : (
                    <>
                      <div className='flex items-center justify-between'>
                        <div>
                          <label className='text-sm font-medium'>Enable In-App Notifications</label>
                          <p className='text-xs text-muted-foreground'>
                            Show notifications in the app
                          </p>
                        </div>
                        <input
                          type='checkbox'
                          checked={preferencesData?.in_app_enabled || false}
                          onChange={e => updatePreferences({ in_app_enabled: e.target.checked })}
                          className='rounded border-gray-300'
                        />
                      </div>

                      <div className='space-y-3 pl-4 border-l-2 border-muted'>
                        <div className='flex items-center justify-between'>
                          <span className='text-sm'>Payment Reminders</span>
                          <input
                            type='checkbox'
                            checked={preferencesData?.in_app_payment_reminders || false}
                            onChange={e =>
                              updatePreferences({ in_app_payment_reminders: e.target.checked })
                            }
                            disabled={!preferencesData?.in_app_enabled}
                            className='rounded border-gray-300'
                          />
                        </div>

                        <div className='flex items-center justify-between'>
                          <span className='text-sm'>Maintenance Updates</span>
                          <input
                            type='checkbox'
                            checked={preferencesData?.in_app_maintenance_updates || false}
                            onChange={e =>
                              updatePreferences({ in_app_maintenance_updates: e.target.checked })
                            }
                            disabled={!preferencesData?.in_app_enabled}
                            className='rounded border-gray-300'
                          />
                        </div>

                        <div className='flex items-center justify-between'>
                          <span className='text-sm'>Lease Updates</span>
                          <input
                            type='checkbox'
                            checked={preferencesData?.in_app_lease_updates || false}
                            onChange={e =>
                              updatePreferences({ in_app_lease_updates: e.target.checked })
                            }
                            disabled={!preferencesData?.in_app_enabled}
                            className='rounded border-gray-300'
                          />
                        </div>

                        <div className='flex items-center justify-between'>
                          <span className='text-sm'>System Updates</span>
                          <input
                            type='checkbox'
                            checked={preferencesData?.in_app_system_updates || false}
                            onChange={e =>
                              updatePreferences({ in_app_system_updates: e.target.checked })
                            }
                            disabled={!preferencesData?.in_app_enabled}
                            className='rounded border-gray-300'
                          />
                        </div>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Digest Settings */}
              <Card className='md:col-span-2'>
                <CardHeader>
                  <CardTitle>Digest Settings</CardTitle>
                  <CardDescription>
                    Choose how often you want to receive notification digests
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {preferencesLoading ? (
                    <LoadingSpinner size='sm' />
                  ) : (
                    <div className='space-y-4'>
                      <div>
                        <label className='text-sm font-medium'>Email Digest Frequency</label>
                        <p className='text-xs text-muted-foreground mb-2'>
                          How often you want to receive email digests of your notifications
                        </p>
                        <select
                          value={preferencesData?.digest_frequency || 'immediate'}
                          onChange={e => updatePreferences({ digest_frequency: e.target.value })}
                          className='w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
                        >
                          <option value='immediate'>Immediate (Real-time)</option>
                          <option value='daily'>Daily</option>
                          <option value='weekly'>Weekly</option>
                          <option value='never'>Never</option>
                        </select>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default NotificationsPage
