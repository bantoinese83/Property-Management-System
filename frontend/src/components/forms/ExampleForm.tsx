import React, { useState } from 'react'
import { Button } from '../common/Button'
import { FormError } from '../common/FormError'
import { LoadingWrapper } from '../common/LoadingWrapper'
import { RetryButton } from '../common/RetryButton'
import { useFormSubmit } from '../../hooks/useFormSubmit'
import client from '../../api/client'

// Example form component showing best practices for error handling
export const ExamplePropertyForm: React.FC = () => {
  const [formData, setFormData] = useState({
    property_name: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
  })

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  const { submit, loading, error, clearError, retry } = useFormSubmit({
    successMessage: 'Property created successfully!',
    onSuccess: _data => {
      // Handle success - maybe redirect or clear form
      setFormData({
        property_name: '',
        address: '',
        city: '',
        state: '',
        zip_code: '',
      })
      setFieldErrors({})
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    setFieldErrors({})

    await submit(async () => {
      const response = await client.post('/properties/', formData)
      return response.data
    })
  }

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear field error when user starts typing
    if (fieldErrors[field]) {
      setFieldErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  return (
    <div className='max-w-md mx-auto p-6'>
      <h2 className='text-2xl font-bold mb-6'>Create Property</h2>

      <LoadingWrapper loading={loading} overlay className='space-y-4'>
        <form onSubmit={handleSubmit} className='space-y-4'>
          {/* Property Name */}
          <div>
            <label className='block text-sm font-medium mb-1'>Property Name *</label>
            <input
              type='text'
              value={formData.property_name}
              onChange={e => handleInputChange('property_name', e.target.value)}
              className='w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
              placeholder='e.g., Downtown Apartments'
            />
            {fieldErrors.property_name && (
              <FormError error={fieldErrors.property_name} className='mt-1' />
            )}
          </div>

          {/* Address */}
          <div>
            <label className='block text-sm font-medium mb-1'>Address *</label>
            <input
              type='text'
              value={formData.address}
              onChange={e => handleInputChange('address', e.target.value)}
              className='w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
              placeholder='e.g., 123 Main St'
            />
            {fieldErrors.address && <FormError error={fieldErrors.address} className='mt-1' />}
          </div>

          {/* City */}
          <div>
            <label className='block text-sm font-medium mb-1'>City *</label>
            <input
              type='text'
              value={formData.city}
              onChange={e => handleInputChange('city', e.target.value)}
              className='w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
              placeholder='e.g., Dallas'
            />
            {fieldErrors.city && <FormError error={fieldErrors.city} className='mt-1' />}
          </div>

          {/* State */}
          <div>
            <label className='block text-sm font-medium mb-1'>State *</label>
            <input
              type='text'
              value={formData.state}
              onChange={e => handleInputChange('state', e.target.value)}
              className='w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
              placeholder='e.g., TX'
              maxLength={50}
            />
            {fieldErrors.state && <FormError error={fieldErrors.state} className='mt-1' />}
          </div>

          {/* ZIP Code */}
          <div>
            <label className='block text-sm font-medium mb-1'>ZIP Code *</label>
            <input
              type='text'
              value={formData.zip_code}
              onChange={e => handleInputChange('zip_code', e.target.value)}
              className='w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
              placeholder='e.g., 75201 or 75201-1234'
              maxLength={10}
            />
            {fieldErrors.zip_code && <FormError error={fieldErrors.zip_code} className='mt-1' />}
          </div>

          {/* General Error */}
          {error && <FormError error={error} className='mb-4' />}

          {/* Submit Buttons */}
          <div className='flex gap-3 pt-4'>
            <Button type='submit' loading={loading} fullWidth>
              {loading ? 'Creating Property...' : 'Create Property'}
            </Button>

            {error && <RetryButton onRetry={retry} loading={loading} text='Retry' size='default' />}
          </div>
        </form>
      </LoadingWrapper>

      {/* Help Text */}
      <div className='mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200'>
        <h3 className='text-sm font-medium text-blue-900 mb-1'>Need Help?</h3>
        <p className='text-sm text-blue-700'>
          All fields marked with * are required. We'll validate your information and provide helpful
          error messages if something needs to be corrected.
        </p>
      </div>
    </div>
  )
}
