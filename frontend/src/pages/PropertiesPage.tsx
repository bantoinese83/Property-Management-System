import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import { Property } from '../types/models'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { Modal } from '../components/common/Modal'
import PropertyForm from '../components/properties/PropertyForm'
import '../styles/pages/PropertiesPage.css'

interface PropertiesResponse {
  results: Property[]
  count: number
  next?: string
  previous?: string
}

const PropertiesPage: React.FC = () => {
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingProperty, setEditingProperty] = useState<Property | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [propertyTypeFilter, setPropertyTypeFilter] = useState('')

  const { data, loading, refetch } = useApi<PropertiesResponse>(
    `${API_ENDPOINTS.PROPERTIES.LIST}?search=${searchTerm}&property_type=${propertyTypeFilter}`
  )

  const properties = data?.results || []

  const handleAddProperty = () => {
    setShowAddModal(true)
  }

  const handleEditProperty = (property: Property) => {
    setEditingProperty(property)
  }

  const handleCloseModal = () => {
    setShowAddModal(false)
    setEditingProperty(null)
    refetch() // Refresh the list
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
          alert('Failed to delete property')
        }
      } catch {
        alert('Error deleting property')
      }
    }
  }

  if (loading) return <div className='loading'>Loading properties...</div>
  if (error) return <div className='error'>Error loading properties: {error.message}</div>

  return (
    <div className='properties-page'>
      <div className='properties-header'>
        <div>
          <h1>Properties</h1>
          <p>Manage your property portfolio</p>
        </div>
        <Button variant='primary' onClick={handleAddProperty}>
          Add Property
        </Button>
      </div>

      <div className='properties-filters'>
        <div className='filter-group'>
          <input
            type='text'
            placeholder='Search properties...'
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className='search-input'
          />
          <select
            value={propertyTypeFilter}
            onChange={e => setPropertyTypeFilter(e.target.value)}
            className='filter-select'
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

      <div className='properties-stats'>
        <div className='stat-card'>
          <h3>Total Properties</h3>
          <span className='stat-number'>{properties.length}</span>
        </div>
        <div className='stat-card'>
          <h3>Active Properties</h3>
          <span className='stat-number'>{properties.filter(p => p.is_active).length}</span>
        </div>
        <div className='stat-card'>
          <h3>Total Units</h3>
          <span className='stat-number'>
            {properties.reduce((sum, p) => sum + p.total_units, 0)}
          </span>
        </div>
        <div className='stat-card'>
          <h3>Avg Occupancy</h3>
          <span className='stat-number'>
            {properties.length > 0
              ? Math.round(
                  properties.reduce((sum, p) => sum + p.occupancy_rate, 0) / properties.length
                )
              : 0}
            %
          </span>
        </div>
      </div>

      <div className='properties-grid'>
        {properties.map(property => (
          <Card
            key={property.id}
            title={property.property_name}
            subtitle={`${property.address}, ${property.city}, ${property.state}`}
            className='property-card'
          >
            <div className='property-info'>
              <div className='property-details'>
                <span className='property-type'>{property.property_type.replace('_', ' ')}</span>
                <span className='property-units'>{property.total_units} units</span>
                <span
                  className={`occupancy-rate ${property.occupancy_rate > 80 ? 'high' : property.occupancy_rate > 50 ? 'medium' : 'low'}`}
                >
                  {property.occupancy_rate}% occupied
                </span>
              </div>
              <div className='property-financial'>
                <div className='monthly-income'>${property.monthly_income}/month</div>
              </div>
            </div>

            <div className='property-actions'>
              <Button variant='ghost' size='sm' onClick={() => handleEditProperty(property)}>
                Edit
              </Button>
              <Button variant='danger' size='sm' onClick={() => handleDeleteProperty(property.id)}>
                Delete
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Add Property Modal */}
      <Modal isOpen={showAddModal} onClose={handleCloseModal} title='Add New Property'>
        <PropertyForm onClose={handleCloseModal} />
      </Modal>

      {/* Edit Property Modal */}
      <Modal isOpen={!!editingProperty} onClose={handleCloseModal} title='Edit Property'>
        {editingProperty && <PropertyForm property={editingProperty} onClose={handleCloseModal} />}
      </Modal>
    </div>
  )
}

export default PropertiesPage
