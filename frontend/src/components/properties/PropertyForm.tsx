import React from 'react'
import { useForm } from '../../hooks/useForm'
import { API_ENDPOINTS } from '../../api/endpoints'
import { Property } from '../../types/models'
import { Button } from '../common/Button'
import { Input } from '../common/Input'
import { Label } from '../common/Label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../common/Select'
import client from '../../api/client'

interface PropertyFormProps {
  property?: Property
  onClose: () => void
}

const PropertyForm: React.FC<PropertyFormProps> = ({ property, onClose }) => {
  const isEditing = !!property

  const { values, errors, loading, handleChange, handleSubmit, setValue } = useForm<Property>({
    initialValues: property || {
      property_name: '',
      description: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      country: 'USA',
      property_type: 'apartment',
      total_units: 1,
      year_built: undefined,
      square_footage: undefined,
      bedrooms: undefined,
      bathrooms: undefined,
      purchase_price: undefined,
      purchase_date: undefined,
      annual_property_tax: undefined,
      insurance_cost: undefined,
      is_active: true,
      is_listed_for_rent: true,
    },
    onSubmit: async formData => {
      try {
        const url = isEditing
          ? API_ENDPOINTS.PROPERTIES.DETAIL(property!.id)
          : API_ENDPOINTS.PROPERTIES.LIST

        const method = isEditing ? 'PUT' : 'POST'

        await client({
          method,
          url,
          data: formData,
        })

        onClose()
      } catch (error) {
        throw new Error(error.response?.data?.detail || 'Failed to save property')
      }
    },
  })

  return (
    <form onSubmit={handleSubmit} className='property-form'>
      <div className='form-grid'>
        {/* Basic Information */}
        <div className='form-section'>
          <h3>Basic Information</h3>

          <Input
            label='Property Name'
            name='property_name'
            value={values.property_name}
            onChange={handleChange}
            error={errors.property_name}
            required
            fullWidth
          />

          <div className='form-row'>
            <div className='form-group'>
              <Label htmlFor='property_type'>Property Type</Label>
              <Select
                value={values.property_type}
                onValueChange={value => setValue('property_type', value)}
              >
                <SelectTrigger className='w-full'>
                  <SelectValue placeholder='Select property type' />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='single_family'>Single Family Home</SelectItem>
                  <SelectItem value='apartment'>Apartment</SelectItem>
                  <SelectItem value='condo'>Condo</SelectItem>
                  <SelectItem value='townhouse'>Townhouse</SelectItem>
                  <SelectItem value='duplex'>Duplex</SelectItem>
                  <SelectItem value='commercial'>Commercial</SelectItem>
                  <SelectItem value='industrial'>Industrial</SelectItem>
                  <SelectItem value='other'>Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Input
              label='Total Units'
              name='total_units'
              type='number'
              value={values.total_units}
              onChange={handleChange}
              min='1'
              required
              fullWidth
            />
          </div>

          <div className='form-group'>
            <label htmlFor='description'>Description</label>
            <textarea
              id='description'
              name='description'
              value={values.description}
              onChange={handleChange}
              rows={3}
              className='form-textarea'
              placeholder='Property description...'
            />
          </div>
        </div>

        {/* Address Information */}
        <div className='form-section'>
          <h3>Address</h3>

          <Input
            label='Street Address'
            name='address'
            value={values.address}
            onChange={handleChange}
            required
            fullWidth
          />

          <div className='form-row'>
            <Input
              label='City'
              name='city'
              value={values.city}
              onChange={handleChange}
              required
              fullWidth
            />

            <Input
              label='State'
              name='state'
              value={values.state}
              onChange={handleChange}
              required
              fullWidth
            />
          </div>

          <div className='form-row'>
            <Input
              label='ZIP Code'
              name='zip_code'
              value={values.zip_code}
              onChange={handleChange}
              required
              fullWidth
            />

            <Input
              label='Country'
              name='country'
              value={values.country}
              onChange={handleChange}
              fullWidth
            />
          </div>
        </div>

        {/* Property Details */}
        <div className='form-section'>
          <h3>Property Details</h3>

          <div className='form-row'>
            <Input
              label='Year Built'
              name='year_built'
              type='number'
              value={values.year_built || ''}
              onChange={handleChange}
              min='1800'
              max={new Date().getFullYear()}
              fullWidth
            />

            <Input
              label='Square Footage'
              name='square_footage'
              type='number'
              value={values.square_footage || ''}
              onChange={handleChange}
              min='0'
              fullWidth
            />
          </div>

          <div className='form-row'>
            <Input
              label='Bedrooms'
              name='bedrooms'
              type='number'
              value={values.bedrooms || ''}
              onChange={handleChange}
              min='0'
              fullWidth
            />

            <Input
              label='Bathrooms'
              name='bathrooms'
              type='number'
              step='0.5'
              value={values.bathrooms || ''}
              onChange={handleChange}
              min='0'
              fullWidth
            />
          </div>
        </div>

        {/* Financial Information */}
        <div className='form-section'>
          <h3>Financial Information</h3>

          <div className='form-row'>
            <Input
              label='Purchase Price'
              name='purchase_price'
              type='number'
              step='0.01'
              value={values.purchase_price || ''}
              onChange={handleChange}
              min='0'
              fullWidth
            />

            <Input
              label='Purchase Date'
              name='purchase_date'
              type='date'
              value={values.purchase_date || ''}
              onChange={handleChange}
              fullWidth
            />
          </div>

          <div className='form-row'>
            <Input
              label='Annual Property Tax'
              name='annual_property_tax'
              type='number'
              step='0.01'
              value={values.annual_property_tax || ''}
              onChange={handleChange}
              min='0'
              fullWidth
            />

            <Input
              label='Insurance Cost'
              name='insurance_cost'
              type='number'
              step='0.01'
              value={values.insurance_cost || ''}
              onChange={handleChange}
              min='0'
              fullWidth
            />
          </div>
        </div>

        {/* Status */}
        <div className='form-section'>
          <h3>Status</h3>

          <div className='form-checkboxes'>
            <label className='checkbox-label'>
              <input
                type='checkbox'
                name='is_active'
                checked={values.is_active}
                onChange={e => setValue('is_active', e.target.checked)}
              />
              Property is active
            </label>

            <label className='checkbox-label'>
              <input
                type='checkbox'
                name='is_listed_for_rent'
                checked={values.is_listed_for_rent}
                onChange={e => setValue('is_listed_for_rent', e.target.checked)}
              />
              Listed for rent
            </label>
          </div>
        </div>
      </div>

      {errors.submit && <div className='form-error'>{errors.submit}</div>}

      <div className='form-actions'>
        <Button type='button' variant='ghost' onClick={onClose}>
          Cancel
        </Button>
        <Button type='submit' variant='primary' loading={loading}>
          {isEditing ? 'Update Property' : 'Add Property'}
        </Button>
      </div>
    </form>
  )
}

export default PropertyForm
