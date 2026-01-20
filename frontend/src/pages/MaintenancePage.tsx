import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import type { MaintenanceRequest } from '../types/models'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { Modal } from '../components/common/Modal'
import { LoadingSpinner, ErrorMessage } from '../components/common'
import { Input } from '../components/common/Input'
import { Wrench, AlertTriangle, Clock, CheckCircle, Plus, User } from 'lucide-react'
import MaintenanceRequestForm from '../components/maintenance/MaintenanceRequestForm'

interface MaintenanceResponse {
  results: MaintenanceRequest[]
  count: number
  next?: string
  previous?: string
}

const MaintenancePage: React.FC = () => {
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingRequest, setEditingRequest] = useState<MaintenanceRequest | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [priorityFilter, setPriorityFilter] = useState('')

  const { data, loading, error, refetch } = useApi<MaintenanceResponse>(
    `${API_ENDPOINTS.MAINTENANCE.LIST}?search=${searchTerm}&status=${statusFilter}&priority=${priorityFilter}`
  )

  const requests = data?.results || []

  const handleAddRequest = () => {
    setShowAddModal(true)
  }

  const handleEditRequest = (request: MaintenanceRequest) => {
    setEditingRequest(request)
  }

  const handleCloseModal = () => {
    setShowAddModal(false)
    setEditingRequest(null)
    refetch() // Refresh the list
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />
      case 'medium':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'low':
        return <Clock className="h-4 w-4 text-blue-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }


  const formatCurrency = (amount: number | undefined) => {
    if (!amount) return '$0.00'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

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
          <div className="flex flex-1 items-center justify-center p-4 lg:p-6">
            <LoadingSpinner size="lg" />
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
            <ErrorMessage message={error.message} title='Failed to load maintenance requests' />
          </div>
        </SidebarInset>
      </SidebarProvider>
    )
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
          {/* Header Section */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Maintenance</h1>
              <p className="text-muted-foreground">
                Manage maintenance requests and property repairs
              </p>
            </div>
            <Button variant="primary" onClick={handleAddRequest}>
              <Plus className="h-4 w-4 mr-2" />
              New Request
            </Button>
          </div>

          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Requests</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl">
                    {requests.length}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Wrench className="h-5 w-5 text-primary" />
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Open Requests</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl">
                    {requests.filter(r => r.status === 'open').length}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <AlertTriangle className="h-5 w-5 text-primary" />
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">In Progress</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl">
                    {requests.filter(r => r.status === 'in_progress').length}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <Clock className="h-5 w-5 text-primary" />
                </div>
              </div>
            </div>

            <div className="rounded-lg border bg-card p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Completed</p>
                  <p className="text-2xl font-bold tabular-nums lg:text-3xl">
                    {requests.filter(r => r.status === 'completed').length}
                  </p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                  <CheckCircle className="h-5 w-5 text-primary" />
                </div>
              </div>
            </div>
          </div>

          {/* Filters Section */}
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-1 items-center space-x-2">
              <Input
                placeholder="Search maintenance requests..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="max-w-sm"
              />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 max-w-xs"
              >
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="assigned">Assigned</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="closed">Closed</option>
              </select>
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 max-w-xs"
              >
                <option value="">All Priorities</option>
                <option value="urgent">Urgent</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>

          {/* Maintenance Requests Grid */}
          {requests.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {requests.map((request) => (
                <Card key={request.id} className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <h3 className="font-semibold leading-none tracking-tight">
                        {request.title}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {request.property_name}
                      </p>
                    </div>
                    <div className="flex items-center gap-1">
                      {getPriorityIcon(request.priority)}
                    </div>
                  </div>

                  <div className="mt-4">
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {request.description}
                    </p>
                  </div>

                  <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Status</p>
                      <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                        request.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : request.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-700'
                          : request.status === 'open'
                          ? 'bg-red-100 text-red-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}>
                        {request.status.replace('_', ' ')}
                      </span>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Priority</p>
                      <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                        request.priority === 'urgent'
                          ? 'bg-red-100 text-red-700'
                          : request.priority === 'high'
                          ? 'bg-orange-100 text-orange-700'
                          : request.priority === 'medium'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}>
                        {request.priority}
                      </span>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Category</p>
                      <p className="font-medium">{request.category}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Est. Cost</p>
                      <p className="font-medium">{formatCurrency(request.estimated_cost)}</p>
                    </div>
                  </div>

                  <div className="mt-4 flex items-center gap-2">
                    {request.tenant_name && (
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <User className="h-3 w-3" />
                        {request.tenant_name}
                      </div>
                    )}
                    {request.is_overdue && (
                      <span className="inline-flex items-center rounded-full bg-red-100 px-2 py-1 text-xs font-medium text-red-700">
                        Overdue
                      </span>
                    )}
                  </div>

                  <div className="mt-6 flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => console.log('Edit request:', request.id)}
                      className="flex-1"
                    >
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => console.log('Update status:', request.id)}
                      className="flex-1"
                    >
                      Update
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => console.log('View details:', request.id)}
                      className="text-destructive hover:text-destructive"
                    >
                      Details
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <Wrench className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mt-4 text-lg font-semibold">No maintenance requests</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                All maintenance issues have been resolved.
              </p>
              <Button className="mt-4" onClick={handleAddRequest}>
                <Plus className="h-4 w-4 mr-2" />
                Report Issue
              </Button>
            </div>
          )}
        </div>
      </SidebarInset>

      {/* Add Maintenance Request Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={handleCloseModal}
        title="New Maintenance Request"
        size="2xl"
      >
        <MaintenanceRequestForm onClose={handleCloseModal} />
      </Modal>

      {/* Edit Maintenance Request Modal */}
      <Modal
        isOpen={!!editingRequest}
        onClose={handleCloseModal}
        title="Edit Maintenance Request"
        size="2xl"
      >
        {editingRequest && (
          <MaintenanceRequestForm
            request={editingRequest}
            onClose={handleCloseModal}
          />
        )}
      </Modal>
    </SidebarProvider>
  )
}

export default MaintenancePage
