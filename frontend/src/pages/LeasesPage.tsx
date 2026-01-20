import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import type { Lease } from '../types/models'
import { toast } from 'sonner'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { Modal } from '../components/common/Modal'
import { LoadingSpinner, ErrorMessage } from '../components/common'
import { Input } from '../components/common/Input'
import { FileText, Calendar, DollarSign, Plus, Download } from 'lucide-react'
import { exportToCSV, entityColumns, type ExportColumn } from '../utils/export'
import LeaseForm from '../components/leases/LeaseForm'

interface LeasesResponse {
  results: Lease[]
  count: number
  next?: string
  previous?: string
}

const LeasesPage: React.FC = () => {
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingLease, setEditingLease] = useState<Lease | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const { data, loading, error, refetch } = useApi<LeasesResponse>(
    `${API_ENDPOINTS.LEASES.LIST}?search=${searchTerm}&status=${statusFilter}`
  )

  const leases = data?.results || []

  const handleAddLease = () => {
    setShowAddModal(true)
  }

  const handleEditLease = (lease: Lease) => {
    setEditingLease(lease)
    setShowAddModal(true) // Reuse the add modal for editing
  }

  const handleCloseModal = () => {
    setShowAddModal(false)
    setEditingLease(null)
    refetch() // Refresh the list
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount)
  }

  const handleExportData = () => {
    if (leases.length === 0) {
      toast.error('No data to export', {
        description: 'There are no leases to export.',
      })
      return
    }

    try {
      exportToCSV(
        leases as unknown as Record<string, unknown>[],
        entityColumns.leases as ExportColumn[],
        'leases'
      )
      toast.success('Export successful', {
        description: 'Leases data has been exported to CSV.',
      })
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Export failed', {
        description: 'An error occurred while exporting data.',
      })
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
            <ErrorMessage message={error.message} title='Failed to load leases' />
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
              <h1 className='text-3xl font-bold tracking-tight'>Leases</h1>
              <p className='text-muted-foreground'>Manage lease agreements and tenant contracts</p>
            </div>
            <div className='flex gap-2'>
              <Button variant='outline' onClick={handleExportData}>
                <Download className='h-4 w-4 mr-2' />
                Export CSV
              </Button>
              <Button variant='primary' onClick={handleAddLease}>
                <Plus className='h-4 w-4 mr-2' />
                Add Lease
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-4'>
            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Total Leases</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>{leases.length}</p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <FileText className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>

            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Active Leases</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>
                    {leases.filter(l => l.status === 'active').length}
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
                  <p className='text-sm font-medium text-muted-foreground'>Ending Soon</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>
                    {leases.filter(l => l.is_ending_soon).length}
                  </p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <Calendar className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>

            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Monthly Revenue</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>
                    $
                    {leases
                      .filter(l => l.status === 'active')
                      .reduce((sum, l) => sum + l.monthly_rent, 0)
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
                placeholder='Search leases...'
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className='max-w-sm'
              />
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
                className='flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 max-w-xs'
              >
                <option value=''>All Statuses</option>
                <option value='draft'>Draft</option>
                <option value='pending'>Pending</option>
                <option value='active'>Active</option>
                <option value='expired'>Expired</option>
                <option value='terminated'>Terminated</option>
              </select>
            </div>
          </div>

          {/* Leases Grid */}
          {leases.length > 0 ? (
            <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
              {leases.map(lease => (
                <Card key={lease.id} className='p-6'>
                  <div className='flex items-start justify-between'>
                    <div className='space-y-1'>
                      <h3 className='font-semibold leading-none tracking-tight'>
                        {lease.property_name}
                      </h3>
                      <p className='text-sm text-muted-foreground'>{lease.tenant_name}</p>
                    </div>
                    <div className='flex h-6 w-6 items-center justify-center rounded-full bg-primary/10'>
                      <FileText className='h-3 w-3 text-primary' />
                    </div>
                  </div>

                  <div className='mt-4 grid grid-cols-2 gap-4 text-sm'>
                    <div>
                      <p className='text-muted-foreground'>Monthly Rent</p>
                      <p className='font-medium'>{formatCurrency(lease.monthly_rent)}</p>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>Status</p>
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                          lease.status === 'active'
                            ? 'bg-green-100 text-green-700'
                            : lease.status === 'pending'
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {lease.status}
                      </span>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>Start Date</p>
                      <p className='font-medium'>
                        {new Date(lease.lease_start_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>End Date</p>
                      <p className='font-medium'>
                        {new Date(lease.lease_end_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  <div className='mt-4 flex items-center gap-2'>
                    {lease.is_ending_soon && (
                      <span className='inline-flex items-center rounded-full bg-orange-100 px-2 py-1 text-xs font-medium text-orange-700'>
                        Ending Soon
                      </span>
                    )}
                    {lease.is_expired && (
                      <span className='inline-flex items-center rounded-full bg-red-100 px-2 py-1 text-xs font-medium text-red-700'>
                        Expired
                      </span>
                    )}
                    <span className='text-xs text-muted-foreground'>
                      {lease.days_remaining > 0
                        ? `${lease.days_remaining} days remaining`
                        : `${Math.abs(lease.days_remaining)} days overdue`}
                    </span>
                  </div>

                  <div className='mt-6 flex gap-2'>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={() => handleEditLease(lease)}
                      className='flex-1'
                    >
                      Edit
                    </Button>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={() =>
                        toast.info('Lease details coming soon!', {
                          description: 'Detailed lease information and history will be available.',
                        })
                      }
                      className='flex-1'
                    >
                      Details
                    </Button>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={() =>
                        toast.info('Lease termination coming soon!', {
                          description:
                            'You will be able to terminate leases and manage terminations.',
                        })
                      }
                      className='text-destructive hover:text-destructive'
                    >
                      Terminate
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <div className='flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center'>
              <div className='flex h-12 w-12 items-center justify-center rounded-full bg-primary/10'>
                <FileText className='h-6 w-6 text-primary' />
              </div>
              <h3 className='mt-4 text-lg font-semibold'>No leases found</h3>
              <p className='mt-2 text-sm text-muted-foreground'>
                Get started by creating your first lease agreement.
              </p>
              <Button className='mt-4'>
                <Plus className='h-4 w-4 mr-2' />
                Create First Lease
              </Button>
            </div>
          )}
        </div>
      </SidebarInset>

      {/* Add Lease Modal */}
      <Modal isOpen={showAddModal} onClose={handleCloseModal} title='Add New Lease' size='2xl'>
        <LeaseForm onClose={handleCloseModal} />
      </Modal>

      {/* Edit Lease Modal */}
      <Modal isOpen={!!editingLease} onClose={handleCloseModal} title='Edit Lease' size='2xl'>
        {editingLease && <LeaseForm lease={editingLease} onClose={handleCloseModal} />}
      </Modal>
    </SidebarProvider>
  )
}

export default LeasesPage
