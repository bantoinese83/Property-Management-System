import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { toast } from 'sonner'
import type { Property } from '../types/models'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { Modal } from '../components/common/Modal'
import { LoadingSpinner, ErrorMessage } from '../components/common'
import PropertyForm from '../components/properties/PropertyForm'
import { DocumentUpload } from '../components/common/DocumentUpload'
import { DocumentList } from '../components/common/DocumentList'
import { Input } from '../components/common/Input'
import { Home, Building2, FileText, BarChart3, Download } from 'lucide-react'
import { exportToCSV, entityColumns, type ExportColumn } from '../utils/export'

interface PropertiesResponse {
  results: Property[]
  count: number
  next?: string
  previous?: string
}

const PropertiesPage: React.FC = () => {
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingProperty, setEditingProperty] = useState<Property | null>(null)
  const [viewingDocuments, setViewingDocuments] = useState<Property | null>(null)
  const [refreshDocsTrigger, setRefreshDocsTrigger] = useState(0)
  const [searchTerm, setSearchTerm] = useState('')
  const [propertyTypeFilter, setPropertyTypeFilter] = useState('')

  const { data, loading, error, refetch } = useApi<PropertiesResponse>(
    `${API_ENDPOINTS.PROPERTIES.LIST}?search=${searchTerm}&property_type=${propertyTypeFilter}`
  )

  const properties = data?.results || []

  const handleAddProperty = () => {
    setShowAddModal(true)
  }

  const handleEditProperty = (property: Property) => {
    setEditingProperty(property)
  }

  const handleViewDocuments = (property: Property) => {
    setViewingDocuments(property)
  }

  const handleCloseModal = () => {
    setShowAddModal(false)
    setEditingProperty(null)
    setViewingDocuments(null)
    refetch() // Refresh the list
  }

  const handleDocumentUploadSuccess = () => {
    setRefreshDocsTrigger(prev => prev + 1)
  }

  const handleExportData = () => {
    if (properties.length === 0) {
      toast.error('No data to export', {
        description: 'There are no properties to export.',
      })
      return
    }

    try {
      exportToCSV(
        properties as unknown as Record<string, unknown>[],
        entityColumns.properties as ExportColumn[],
        'properties'
      )
      toast.success('Export successful', {
        description: 'Properties data has been exported to CSV.',
      })
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Export failed', {
        description: 'An error occurred while exporting data.',
      })
    }
  }

  const handleDeleteProperty = async (propertyId: number) => {
    if (window.confirm('Are you sure you want to delete this property?')) {
      try {
        const response = await fetch(`${API_ENDPOINTS.PROPERTIES.LIST}${propertyId}/`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        })

        if (response.ok) {
          refetch() // Refresh the list
        } else {
          toast.error('Failed to delete property', {
            description: 'Please try again or contact support if the problem persists.',
          })
        }
      } catch {
        toast.error('Error deleting property', {
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
            <ErrorMessage message={error.message} title='Failed to load properties' />
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
              <h1 className='text-3xl font-bold tracking-tight'>Properties</h1>
              <p className='text-muted-foreground'>Manage your property portfolio</p>
            </div>
            <div className='flex gap-2'>
              <Button variant='outline' onClick={handleExportData}>
                <Download className='h-4 w-4 mr-2' />
                Export CSV
              </Button>
              <Button variant='primary' onClick={handleAddProperty}>
                Add Property
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-4'>
            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Total Properties</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>{properties.length}</p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <Home className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>

            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Active Properties</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>
                    {properties.filter(p => p.is_active).length}
                  </p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <Building2 className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>

            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Total Units</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>
                    {properties.reduce((sum, p) => sum + p.total_units, 0)}
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
                  <p className='text-sm font-medium text-muted-foreground'>Avg Occupancy</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>
                    {properties.length > 0
                      ? Math.round(
                          properties.reduce((sum, p) => sum + p.occupancy_rate, 0) /
                            properties.length
                        )
                      : 0}
                    %
                  </p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <BarChart3 className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>
          </div>

          {/* Filters Section */}
          <div className='flex flex-col gap-4 md:flex-row md:items-center md:justify-between'>
            <div className='flex flex-1 items-center space-x-2'>
              <Input
                placeholder='Search properties...'
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className='max-w-sm'
              />
              <select
                value={propertyTypeFilter}
                onChange={e => setPropertyTypeFilter(e.target.value)}
                className='flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 max-w-xs'
              >
                <option value=''>All Types</option>
                <option value='single_family'>Single Family</option>
                <option value='apartment'>Apartment</option>
                <option value='condo'>Condo</option>
                <option value='townhouse'>Townhouse</option>
                <option value='commercial'>Commercial</option>
                <option value='other'>Other</option>
              </select>
            </div>
          </div>

          {/* Properties Grid */}
          {properties.length > 0 ? (
            <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
              {properties.map(property => (
                <Card key={property.id} className='p-6'>
                  <div className='flex items-start justify-between'>
                    <div className='space-y-1'>
                      <h3 className='font-semibold leading-none tracking-tight'>
                        {property.property_name}
                      </h3>
                      <p className='text-sm text-muted-foreground'>
                        {property.address}, {property.city}, {property.state}
                      </p>
                    </div>
                    <div className='flex h-6 w-6 items-center justify-center rounded-full bg-primary/10'>
                      <Home className='h-3 w-3 text-primary' />
                    </div>
                  </div>

                  <div className='mt-4 grid grid-cols-2 gap-4 text-sm'>
                    <div>
                      <p className='text-muted-foreground'>Type</p>
                      <p className='font-medium capitalize'>
                        {property.property_type.replace('_', ' ')}
                      </p>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>Units</p>
                      <p className='font-medium'>{property.total_units}</p>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>Occupancy</p>
                      <p className='font-medium'>{property.occupancy_rate}%</p>
                    </div>
                    <div>
                      <p className='text-muted-foreground'>Monthly Income</p>
                      <p className='font-medium'>${property.monthly_income}</p>
                    </div>
                  </div>

                  <div className='mt-6 flex gap-2'>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={() => handleEditProperty(property)}
                      className='flex-1'
                    >
                      Edit
                    </Button>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={() => handleViewDocuments(property)}
                      className='flex-1'
                    >
                      Documents
                    </Button>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={() => handleDeleteProperty(property.id)}
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
                <Home className='h-6 w-6 text-primary' />
              </div>
              <h3 className='mt-4 text-lg font-semibold'>No properties found</h3>
              <p className='mt-2 text-sm text-muted-foreground'>
                Get started by adding your first property.
              </p>
              <Button className='mt-4' onClick={handleAddProperty}>
                Add Your First Property
              </Button>
            </div>
          )}
        </div>
      </SidebarInset>

      {/* Add Property Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={handleCloseModal}
        title='Add New Property'
        description='Create a new property in your portfolio'
      >
        <PropertyForm onClose={handleCloseModal} />
      </Modal>

      {/* Edit Property Modal */}
      <Modal
        isOpen={!!editingProperty}
        onClose={handleCloseModal}
        title='Edit Property'
        description='Update property information and settings'
      >
        {editingProperty && <PropertyForm property={editingProperty} onClose={handleCloseModal} />}
      </Modal>

      {/* View Documents Modal */}
      <Modal
        isOpen={!!viewingDocuments}
        onClose={handleCloseModal}
        title={`Documents - ${viewingDocuments?.property_name}`}
        description='Manage documents for this property'
      >
        {viewingDocuments && (
          <div className='space-y-6'>
            <DocumentUpload
              modelName='property'
              objectId={viewingDocuments.id}
              onUploadSuccess={handleDocumentUploadSuccess}
            />
            <DocumentList
              modelName='property'
              objectId={viewingDocuments.id}
              refreshTrigger={refreshDocsTrigger}
            />
          </div>
        )}
      </Modal>
    </SidebarProvider>
  )
}

export default PropertiesPage
