import React from 'react'
import { type AxiosError } from 'axios'
import { useForm } from '../../hooks/useForm'
import { API_ENDPOINTS } from '../../api/endpoints'
import { type Tenant } from '../../types/models'
import { Button } from '../common/Button'
import { Input } from '../common/Input'
import client from '../../api/client'

interface TenantFormProps {
  tenant?: Tenant
  onClose: () => void
}

type TenantFormValues = Omit<
  Tenant,
  'id' | 'full_name' | 'active_lease_count' | 'monthly_rent_total' | 'created_at' | 'updated_at'
>

const TenantForm: React.FC<TenantFormProps> = ({ tenant, onClose }) => {
  const isEditing = !!tenant

  const { values, errors, loading, handleChange, handleSubmit, setValue } =
    useForm<TenantFormValues>({
      initialValues: (tenant as TenantFormValues) || {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        date_of_birth: undefined,
        address: '',
        city: '',
        state: '',
        zip_code: '',
        emergency_contact_name: '',
        emergency_contact_phone: '',
        emergency_contact_relationship: '',
        employer_name: '',
        employer_phone: '',
        annual_income: undefined,
        previous_landlord_name: '',
        previous_landlord_phone: '',
        is_active: true,
        credit_score: undefined,
      },
      onSubmit: async formData => {
        try {
          const url = isEditing
            ? API_ENDPOINTS.TENANTS.DETAIL(tenant!.id)
            : API_ENDPOINTS.TENANTS.LIST

          const method = isEditing ? 'PUT' : 'POST'

          await client({
            method,
            url,
            data: formData,
          })

          onClose()
        } catch (error) {
          const axiosError = error as AxiosError<{ detail?: string }>
          throw new Error(axiosError.response?.data?.detail || 'Failed to save tenant')
        }
      },
    })

  return (
    <form onSubmit={handleSubmit} className='space-y-5'>
      {/* Basic Information */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>Basic Information</h3>
          <p className='text-xs text-muted-foreground'>Personal details and contact information</p>
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
          <Input
            label='First Name'
            name='first_name'
            value={values.first_name}
            onChange={handleChange}
            error={errors.first_name}
            required
          />

          <Input
            label='Last Name'
            name='last_name'
            value={values.last_name}
            onChange={handleChange}
            error={errors.last_name}
            required
          />
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
          <Input
            label='Email'
            name='email'
            type='email'
            value={values.email}
            onChange={handleChange}
            error={errors.email}
            required
          />

          <Input
            label='Phone'
            name='phone'
            type='tel'
            value={values.phone}
            onChange={handleChange}
          />
        </div>

        <Input
          label='Date of Birth'
          name='date_of_birth'
          type='date'
          value={values.date_of_birth || ''}
          onChange={handleChange}
        />
      </div>

      {/* Address Information */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>Address</h3>
          <p className='text-xs text-muted-foreground'>Current residential address</p>
        </div>

        <Input
          label='Street Address'
          name='address'
          value={values.address}
          onChange={handleChange}
        />

        <div className='grid grid-cols-1 md:grid-cols-3 gap-3'>
          <Input label='City' name='city' value={values.city} onChange={handleChange} />

          <Input label='State' name='state' value={values.state} onChange={handleChange} />

          <Input label='ZIP Code' name='zip_code' value={values.zip_code} onChange={handleChange} />
        </div>
      </div>

      {/* Emergency Contact */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>Emergency Contact</h3>
          <p className='text-xs text-muted-foreground'>Contact person in case of emergency</p>
        </div>

        <Input
          label='Contact Name'
          name='emergency_contact_name'
          value={values.emergency_contact_name}
          onChange={handleChange}
        />

        <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
          <Input
            label='Contact Phone'
            name='emergency_contact_phone'
            type='tel'
            value={values.emergency_contact_phone}
            onChange={handleChange}
          />

          <Input
            label='Relationship'
            name='emergency_contact_relationship'
            value={values.emergency_contact_relationship}
            onChange={handleChange}
          />
        </div>
      </div>

      {/* Employment Information */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>Employment</h3>
          <p className='text-xs text-muted-foreground'>Employment details and income</p>
        </div>

        <Input
          label='Employer Name'
          name='employer_name'
          value={values.employer_name}
          onChange={handleChange}
        />

        <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
          <Input
            label='Employer Phone'
            name='employer_phone'
            type='tel'
            value={values.employer_phone}
            onChange={handleChange}
          />

          <Input
            label='Annual Income'
            name='annual_income'
            type='number'
            value={values.annual_income || ''}
            onChange={handleChange}
            min='0'
          />
        </div>
      </div>

      {/* References */}
      <div className='space-y-3'>
        <div>
          <h3 className='text-base font-medium text-foreground'>References</h3>
          <p className='text-xs text-muted-foreground'>Previous landlord and credit info</p>
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-3'>
          <Input
            label='Previous Landlord Name'
            name='previous_landlord_name'
            value={values.previous_landlord_name}
            onChange={handleChange}
          />

          <Input
            label='Previous Landlord Phone'
            name='previous_landlord_phone'
            type='tel'
            value={values.previous_landlord_phone}
            onChange={handleChange}
          />
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
          <Input
            label='Credit Score'
            name='credit_score'
            type='number'
            value={values.credit_score || ''}
            onChange={handleChange}
            min='300'
            max='850'
          />

          <div className='flex items-center space-x-2 pt-6'>
            <input
              type='checkbox'
              id='is_active'
              name='is_active'
              checked={values.is_active}
              onChange={e => setValue('is_active', e.target.checked)}
              className='h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded'
            />
            <label htmlFor='is_active' className='text-sm font-medium text-foreground'>
              Tenant is active
            </label>
          </div>
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
          {isEditing ? 'Update Tenant' : 'Add Tenant'}
        </Button>
      </div>
    </form>
  )
}

export default TenantForm
