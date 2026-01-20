import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { toast } from 'sonner'
import type { Tenant } from '../types/models'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { Modal } from '../components/common/Modal'
import { LoadingSpinner, ErrorMessage } from '../components/common'
import TenantForm from '../components/tenants/TenantForm'
import { DocumentUpload } from '../components/common/DocumentUpload'
import { DocumentList } from '../components/common/DocumentList'
import { Input } from '../components/common/Input'
import { Users, FileText, DollarSign, Download } from 'lucide-react'
import { exportToCSV, entityColumns } from '../utils/export'

interface TenantsResponse {
  results: Tenant[]
  count: number
  next?: string
  previous?: string
}

const TenantsPage: React.FC = () => {
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null)
  const [viewingDocuments, setViewingDocuments] = useState<Tenant | null>(null)
  const [refreshDocsTrigger, setRefreshDocsTrigger] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')

  const { data, loading, error, refetch } = useApi<TenantsResponse>(
    `${API_ENDPOINTS.TENANTS.LIST}?search=${searchTerm}`
  )

  const tenants = data?.results || []

  const handleAddTenant = () => {
    setShowAddModal(true)
  }

  const handleEditTenant = (tenant: Tenant) => {
    setEditingTenant(tenant)
  }

  const handleViewDocuments = (tenant: Tenant) => {
    setViewingDocuments(tenant)
  }

  const handleCloseModal = () => {
    setShowAddModal(false)
    setEditingTenant(null)
    setViewingDocuments(null)
    refetch() // Refresh the list
  }

  const handleDocumentUploadSuccess = () => {
    setRefreshDocsTrigger(prev => prev + 1)
  }

  const handleExportData = () => {
    if (tenants.length === 0) {
      toast.error('No data to export', {
        description: 'There are no tenants to export.'
      })
      return
    }

    try {
      exportToCSV(tenants, entityColumns.tenants, 'tenants')
      toast.success('Export successful', {
        description: 'Tenants data has been exported to CSV.'
      })
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Export failed', {
        description: 'An error occurred while exporting data.'
      })
    }
  }

  const handleDeleteTenant = async (tenantId: number) => {
    if (window.confirm('Are you sure you want to delete this tenant?')) {
      try {
        const response = await fetch(`${API_ENDPOINTS.TENANTS.LIST}${tenantId}/`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        })

        if (response.ok) {
          refetch() // Refresh the list
        } else {
          toast.error('Failed to delete tenant', {
            description: 'Please try again or contact support if the problem persists.',
          })
        }
      } catch {
        toast.error('Error deleting tenant', {
          description: 'An unexpected error occurred.',
        })
      }
    }
  }

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
            <ErrorMessage message={error.message} title='Failed to load tenants' />
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
          {/* Header Section */}
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold tracking-tight'>Tenants</h1>
              <p className='text-muted-foreground'>Manage tenant information and profiles</p>
            </div>
            <div className='flex gap-2'>
              <Button variant='outline' onClick={handleExportData}>
                <Download className='h-4 w-4 mr-2' />
                Export CSV
              </Button>
              <Button variant='primary' onClick={handleAddTenant}>
                Add Tenant
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-4'>
            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Total Tenants</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>{tenants.length}</p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <Users className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>

            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Active Tenants</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>
                    {tenants.filter(t => t.is_active).length}
                  </p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <Users className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>

            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Active Leases</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>
                    {tenants.reduce((sum, t) => sum + t.active_lease_count, 0)}
                  </p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <FileText className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>

            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Monthly Revenue</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>
                    $
                    {tenants
                      .reduce((sum, t) => sum + parseFloat(t.monthly_rent_total), 0)
                      .toLocaleString()}
                  </p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <DollarSign className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>
          </div>

          {/* Filters Section */}
          <div className='flex flex-col gap-4 md:flex-row md:items-center md:justify-between'>
            <div className='flex flex-1 items-center space-x-2'>
              <Input
                placeholder='Search tenants...'
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className='max-w-sm'
              />
            </div>
          </div>

          {/* Tenants Grid */}
          {tenants.length > 0 ? (
            <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
              {tenants.map(tenant => (
                <Card key={tenant.id} className='p-6'>
                  <div className='flex items-start justify-between'>
                    <div className='space-y-1'>
                      <h3 className='font-semibold leading-none tracking-tight'>
                        {tenant.full_name}
                      </h3>
                      <p className='text-sm text-muted-foreground'>{tenant.email}</p>
                    </div>
                    <div className='flex h-6 w-6 items-center justify-center rounded-full bg-primary/10'>
                      <Users className='h-3 w-3 text-primary' />
                    </div>
                  </div>

                  <div className='mt-4 grid grid-cols-2 gap-4 text-sm'>
                    <div>
                      <p className='text-muted-foreground'>Phone</p>
                      <p className='font-medium'>{tenant.phone}</p>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>Location</p>
                      <p className='font-medium'>
                        {tenant.city}, {tenant.state}
                      </p>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>Active Leases</p>
                      <p className='font-medium'>{tenant.active_lease_count}</p>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>Monthly Rent</p>
                      <p className='font-medium'>${tenant.monthly_rent_total}</p>
                    </div>
                  </div>

                  <div className='mt-4 flex items-center gap-2'>
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                        tenant.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {tenant.is_active ? 'Active' : 'Inactive'}
                    </span>
                    {tenant.credit_score && (
                      <span className='text-xs text-muted-foreground'>
                        Credit: {tenant.credit_score}
                      </span>
                    )}
                  </div>

                  <div className='mt-6 flex gap-2'>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={() => handleEditTenant(tenant)}
                      className='flex-1'
                    >
                      Edit
                    </Button>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={() => handleViewDocuments(tenant)}
                      className='flex-1'
                    >
                      Documents
                    </Button>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={() => handleDeleteTenant(tenant.id)}
                      className='text-destructive hover:text-destructive'
                    >
                      Delete
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <div className='flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center'>
              <div className='flex h-12 w-12 items-center justify-center rounded-full bg-primary/10'>
                <Users className='h-6 w-6 text-primary' />
              </div>
              <h3 className='mt-4 text-lg font-semibold'>No tenants found</h3>
              <p className='mt-2 text-sm text-muted-foreground'>
                Get started by adding your first tenant.
              </p>
              <Button className='mt-4' onClick={handleAddTenant}>
                Add Your First Tenant
              </Button>
            </div>
          )}
        </div>
      </SidebarInset>

      {/* Add Tenant Modal */}
      <Modal isOpen={showAddModal} onClose={handleCloseModal} title='Add New Tenant' size='2xl'>
        <TenantForm onClose={handleCloseModal} />
      </Modal>

      {/* Edit Tenant Modal */}
      <Modal isOpen={!!editingTenant} onClose={handleCloseModal} title='Edit Tenant' size='2xl'>
        {editingTenant && <TenantForm tenant={editingTenant} onClose={handleCloseModal} />}
      </Modal>

      {/* View Documents Modal */}
      <Modal
        isOpen={!!viewingDocuments}
        onClose={handleCloseModal}
        title={`Documents - ${viewingDocuments?.full_name}`}
      >
        {viewingDocuments && (
          <div className='space-y-6'>
            <DocumentUpload
              modelName='tenant'
              objectId={viewingDocuments.id}
              onUploadSuccess={handleDocumentUploadSuccess}
            />
            <DocumentList
              modelName='tenant'
              objectId={viewingDocuments.id}
              refreshTrigger={refreshDocsTrigger}
            />
          </div>
        )}
      </Modal>
    </SidebarProvider>
  )
}

export default TenantsPage
