import React from 'react'
import { type AxiosError } from 'axios'
import { useForm } from '../../hooks/useForm'
import { API_ENDPOINTS } from '../../api/endpoints'
import { type MaintenanceRequest } from '../../types/models'
import { Button } from '../common/Button'
import { Input } from '../common/Input'
import client from '../../api/client'

interface MaintenanceRequestFormProps {
  request?: MaintenanceRequest
  onClose: () => void
}

type MaintenanceRequestFormValues = Omit<
  MaintenanceRequest,
  | 'id'
  | 'tenant_name'
  | 'property_name'
  | 'requested_by_name'
  | 'assigned_to_name'
  | 'created_at'
  | 'updated_at'
  | 'is_overdue'
  | 'days_since_request'
> & {
  property_obj?: number
}

const MaintenanceRequestForm: React.FC<MaintenanceRequestFormProps> = ({ request, onClose }) => {
  const isEditing = !!request

  const {
    values,
    errors,
    loading,
    handleChange,
    handleSubmit,
    setValue: _setValue,
  } = useForm<MaintenanceRequestFormValues>({
    initialValues: (request as MaintenanceRequestFormValues) || {
      property_obj: undefined,
      tenant: undefined,
      title: '',
      description: '',
      priority: 'medium',
      category: '',
      status: 'open',
      assigned_to: undefined,
      vendor_name: '',
      vendor_phone: '',
      vendor_email: '',
      estimated_cost: undefined,
      actual_cost: undefined,
      requested_date: '',
      scheduled_date: '',
      completed_date: '',
      images: [],
      notes: '',
    },
    onSubmit: async formData => {
      try {
        const url = isEditing
          ? API_ENDPOINTS.MAINTENANCE.DETAIL(request!.id)
          : API_ENDPOINTS.MAINTENANCE.LIST

        const method = isEditing ? 'PUT' : 'POST'

        await client({
          method,
          url,
          data: formData,
        })

        onClose()
      } catch (error) {
        const axiosError = error as AxiosError<{ detail?: string }>
        throw new Error(axiosError.response?.data?.detail || 'Failed to save maintenance request')
      }
    },
  })

  const priorityOptions = [
    { value: 'low', label: 'Low - General maintenance' },
    { value: 'medium', label: 'Medium - Needs attention soon' },
    { value: 'high', label: 'High - Urgent repair needed' },
    { value: 'urgent', label: 'Urgent - Emergency situation' },
  ]

  const categoryOptions = [
    { value: 'plumbing', label: 'Plumbing' },
    { value: 'electrical', label: 'Electrical' },
    { value: 'hvac', label: 'HVAC' },
    { value: 'structural', label: 'Structural' },
    { value: 'appliance', label: 'Appliance' },
    { value: 'pest_control', label: 'Pest Control' },
    { value: 'landscaping', label: 'Landscaping' },
    { value: 'security', label: 'Security' },
    { value: 'cleaning', label: 'Cleaning' },
    { value: 'other', label: 'Other' },
  ]

  return (
    <form onSubmit={handleSubmit} className='space-y-5'>
      {/* Request Details */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>Request Details</h3>
          <p className='text-xs text-muted-foreground'>
            Basic information about the maintenance request
          </p>
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
          <Input
            label='Property ID'
            name='property_obj'
            type='number'
            value={values.property_obj || ''}
            onChange={handleChange}
            required
          />

          <Input
            label='Tenant ID (Optional)'
            name='tenant'
            type='number'
            value={values.tenant || ''}
            onChange={handleChange}
          />
        </div>

        <Input
          label='Title'
          name='title'
          value={values.title}
          onChange={handleChange}
          placeholder='Brief description of the issue'
          required
        />

        <div>
          <label className='text-sm font-medium text-muted-foreground mb-2 block'>
            Description
          </label>
          <textarea
            name='description'
            value={values.description}
            onChange={handleChange}
            rows={4}
            className='flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
            placeholder='Detailed description of the maintenance issue...'
            required
          />
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
          <div>
            <label className='text-sm font-medium text-muted-foreground mb-2 block'>Priority</label>
            <select
              name='priority'
              value={values.priority}
              onChange={handleChange}
              className='flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
              required
            >
              {priorityOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className='text-sm font-medium text-muted-foreground mb-2 block'>Category</label>
            <select
              name='category'
              value={values.category}
              onChange={handleChange}
              className='flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
              required
            >
              <option value=''>Select Category</option>
              {categoryOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Scheduling */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>Scheduling</h3>
          <p className='text-xs text-muted-foreground'>Request and scheduling dates</p>
        </div>

        <div className='grid grid-cols-1 md:grid-cols-3 gap-3'>
          <Input
            label='Requested Date'
            name='requested_date'
            type='date'
            value={values.requested_date}
            onChange={handleChange}
            required
          />

          <Input
            label='Scheduled Date'
            name='scheduled_date'
            type='date'
            value={values.scheduled_date || ''}
            onChange={handleChange}
          />

          <Input
            label='Completed Date'
            name='completed_date'
            type='date'
            value={values.completed_date || ''}
            onChange={handleChange}
          />
        </div>
      </div>

      {/* Cost Information */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>Cost Information</h3>
          <p className='text-xs text-muted-foreground'>Estimated and actual costs</p>
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
          <Input
            label='Estimated Cost'
            name='estimated_cost'
            type='number'
            value={values.estimated_cost || ''}
            onChange={handleChange}
            min='0'
            step='0.01'
          />

          <Input
            label='Actual Cost'
            name='actual_cost'
            type='number'
            value={values.actual_cost || ''}
            onChange={handleChange}
            min='0'
            step='0.01'
          />
        </div>
      </div>

      {/* Vendor Information */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>Vendor Information</h3>
          <p className='text-xs text-muted-foreground'>Contact details for assigned vendor</p>
        </div>

        <Input
          label='Vendor Name'
          name='vendor_name'
          value={values.vendor_name}
          onChange={handleChange}
        />

        <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
          <Input
            label='Vendor Phone'
            name='vendor_phone'
            type='tel'
            value={values.vendor_phone}
            onChange={handleChange}
          />

          <Input
            label='Vendor Email'
            name='vendor_email'
            type='email'
            value={values.vendor_email}
            onChange={handleChange}
          />
        </div>
      </div>

      {/* Assignment */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>Assignment</h3>
          <p className='text-xs text-muted-foreground'>
            Assign the request to a maintenance person
          </p>
        </div>

        <Input
          label='Assigned To (User ID)'
          name='assigned_to'
          type='number'
          value={values.assigned_to || ''}
          onChange={handleChange}
        />
      </div>

      {/* Additional Notes */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>Additional Notes</h3>
          <p className='text-xs text-muted-foreground'>Any additional information or notes</p>
        </div>

        <div>
          <label className='text-sm font-medium text-muted-foreground mb-2 block'>Notes</label>
          <textarea
            name='notes'
            value={values.notes}
            onChange={handleChange}
            rows={3}
            className='flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
            placeholder='Additional notes about the maintenance request...'
          />
        </div>
      </div>

      {/* Error Display */}
      {errors.submit && (
        <div className='rounded-lg border border-red-200 bg-red-50 p-4 text-red-800'>
          {errors.submit}
        </div>
      )}

      {/* Form Actions */}
      <div className='flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 pt-4'>
        <Button type='button' variant='ghost' onClick={onClose} className='mt-2 sm:mt-0'>
          Cancel
        </Button>
        <Button type='submit' variant='primary' loading={loading}>
          {isEditing ? 'Update Request' : 'Create Request'}
        </Button>
      </div>
    </form>
  )
}

export default MaintenanceRequestForm
