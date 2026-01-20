import React from 'react'
import { type AxiosError } from 'axios'
import { useForm } from '../../hooks/useForm'
import { API_ENDPOINTS } from '../../api/endpoints'
import { type Property } from '../../types/models'
import { Button } from '../common/Button'
import { Input } from '../common/Input'
import { Label } from '../common/Label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../common/Select'
import client from '../../api/client'

interface PropertyFormProps {
  property?: Property
  onClose: () => void
}

type PropertyFormValues = Omit<
  Property,
  | 'id'
  | 'owner'
  | 'owner_name'
  | 'full_address'
  | 'monthly_income'
  | 'occupancy_rate'
  | 'images'
  | 'created_at'
  | 'updated_at'
>

const PropertyForm: React.FC<PropertyFormProps> = ({ property, onClose }) => {
  const isEditing = !!property

  const { values, errors, loading, handleChange, handleSubmit, setValue } =
    useForm<PropertyFormValues>({
      initialValues: (property as PropertyFormValues) || {
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
          const axiosError = error as AxiosError<{ detail?: string }>
          throw new Error(axiosError.response?.data?.detail || 'Failed to save property')
        }
      },
    })

  return (
    <form onSubmit={handleSubmit} className='space-y-6'>
      <div className='grid gap-6 lg:grid-cols-2'>
        {/* Basic Information */}
        <div className='space-y-4 lg:col-span-2'>
          <h3 className='text-lg font-semibold border-b pb-2'>Basic Information</h3>

          <Input
            label='Property Name'
            name='property_name'
            value={values.property_name}
            onChange={handleChange}
            error={errors.property_name}
            required
            fullWidth
          />

          <div className='grid gap-4 sm:grid-cols-2'>
            <div className='space-y-2'>
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

          <div className='space-y-2'>
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
        <div className='space-y-4 lg:col-span-2'>
          <h3 className='text-lg font-semibold border-b pb-2'>Address</h3>

          <Input
            label='Street Address'
            name='address'
            value={values.address}
            onChange={handleChange}
            required
            fullWidth
          />

          <div className='grid gap-4 sm:grid-cols-2'>
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

          <div className='grid gap-4 sm:grid-cols-2'>
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
        <div className='space-y-4 lg:col-span-2'>
          <h3 className='text-lg font-semibold border-b pb-2'>Property Details</h3>

          <div className='grid gap-4 sm:grid-cols-2'>
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

          <div className='grid gap-4 sm:grid-cols-2'>
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
        <div className='space-y-4 lg:col-span-2'>
          <h3 className='text-lg font-semibold border-b pb-2'>Financial Information</h3>

          <div className='grid gap-4 sm:grid-cols-2'>
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

          <div className='grid gap-4 sm:grid-cols-2'>
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
        <div className='space-y-4 lg:col-span-2'>
          <h3 className='text-lg font-semibold border-b pb-2'>Status</h3>

          <div className='space-y-3'>
            <label className='flex items-center space-x-2 cursor-pointer'>
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

      <div className='flex flex-col-reverse sm:flex-row gap-3 sm:justify-end pt-6 border-t'>
        <Button type='button' variant='ghost' onClick={onClose} className='w-full sm:w-auto'>
          Cancel
        </Button>
        <Button type='submit' variant='primary' loading={loading} className='w-full sm:w-auto'>
          {isEditing ? 'Update Property' : 'Add Property'}
        </Button>
      </div>
    </form>
  )
}

export default PropertyForm
