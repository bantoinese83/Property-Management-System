import React from 'react'
import { type AxiosError } from 'axios'
import { useForm } from '../../hooks/useForm'
import { API_ENDPOINTS } from '../../api/endpoints'
import { type Lease } from '../../types/models'
import { Button } from '../common/Button'
import { Input } from '../common/Input'
import client from '../../api/client'

interface LeaseFormProps {
  lease?: Lease
  onClose: () => void
}

type LeaseFormValues = Omit<
  Lease,
  'id' | 'tenant_name' | 'property_name' | 'days_remaining' | 'is_ending_soon' | 'is_expired' | 'created_at' | 'updated_at'
>

const LeaseForm: React.FC<LeaseFormProps> = ({ lease, onClose }) => {
  const isEditing = !!lease

  const { values, errors, loading, handleChange, handleSubmit, setValue } =
    useForm<LeaseFormValues>({
      initialValues: (lease as LeaseFormValues) || {
        property_obj: undefined,
        tenant: undefined,
        lease_start_date: '',
        lease_end_date: '',
        signed_date: '',
        monthly_rent: undefined,
        deposit_amount: undefined,
        pet_deposit: 0,
        late_fee: 0,
        lease_document_url: '',
        status: 'draft',
        auto_renew: true,
        renewal_notice_days: 30,
        notes: '',
      },
      onSubmit: async formData => {
        try {
          const url = isEditing
            ? API_ENDPOINTS.LEASES.DETAIL(lease!.id)
            : API_ENDPOINTS.LEASES.LIST

          const method = isEditing ? 'PUT' : 'POST'

          await client({
            method,
            url,
            data: formData,
          })

          onClose()
        } catch (error) {
          const axiosError = error as AxiosError<{ detail?: string }>
          throw new Error(axiosError.response?.data?.detail || 'Failed to save lease')
        }
      },
    })

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Lease Details */}
      <div className="space-y-3">
        <div>
          <h3 className="text-base font-medium text-foreground">Lease Details</h3>
          <p className="text-xs text-muted-foreground">Basic lease information and dates</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input
            label="Property ID"
            name="property_obj"
            type="number"
            value={values.property_obj || ''}
            onChange={handleChange}
            required
          />

          <Input
            label="Tenant ID"
            name="tenant"
            type="number"
            value={values.tenant || ''}
            onChange={handleChange}
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input
            label="Start Date"
            name="lease_start_date"
            type="date"
            value={values.lease_start_date}
            onChange={handleChange}
            required
          />

          <Input
            label="End Date"
            name="lease_end_date"
            type="date"
            value={values.lease_end_date}
            onChange={handleChange}
            required
          />
        </div>

        <Input
          label="Signed Date"
          name="signed_date"
          type="date"
          value={values.signed_date || ''}
          onChange={handleChange}
        />
      </div>

      {/* Financial Information */}
      <div className="space-y-3">
        <div>
          <h3 className="text-base font-medium text-foreground">Financial Information</h3>
          <p className="text-xs text-muted-foreground">Rent and deposit amounts</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input
            label="Monthly Rent"
            name="monthly_rent"
            type="number"
            value={values.monthly_rent || ''}
            onChange={handleChange}
            min="0"
            step="0.01"
            required
          />

          <Input
            label="Security Deposit"
            name="deposit_amount"
            type="number"
            value={values.deposit_amount || ''}
            onChange={handleChange}
            min="0"
            step="0.01"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input
            label="Pet Deposit"
            name="pet_deposit"
            type="number"
            value={values.pet_deposit || ''}
            onChange={handleChange}
            min="0"
            step="0.01"
          />

          <Input
            label="Late Fee"
            name="late_fee"
            type="number"
            value={values.late_fee || ''}
            onChange={handleChange}
            min="0"
            step="0.01"
          />
        </div>
      </div>

      {/* Settings */}
      <div className="space-y-3">
        <div>
          <h3 className="text-base font-medium text-foreground">Settings</h3>
          <p className="text-xs text-muted-foreground">Lease configuration and status</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="text-sm font-medium text-muted-foreground mb-2 block">
              Status
            </label>
            <select
              name="status"
              value={values.status}
              onChange={handleChange}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option value="draft">Draft</option>
              <option value="pending">Pending Signature</option>
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="terminated">Terminated</option>
            </select>
          </div>

          <Input
            label="Renewal Notice Days"
            name="renewal_notice_days"
            type="number"
            value={values.renewal_notice_days || ''}
            onChange={handleChange}
            min="1"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="flex items-center space-x-2 pt-6">
            <input
              type="checkbox"
              id="auto_renew"
              name="auto_renew"
              checked={values.auto_renew}
              onChange={e => setValue('auto_renew', e.target.checked)}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            />
            <label htmlFor="auto_renew" className="text-sm font-medium text-foreground">
              Auto-renew lease
            </label>
          </div>
        </div>
      </div>

      {/* Additional Information */}
      <div className="space-y-3">
        <div>
          <h3 className="text-base font-medium text-foreground">Additional Information</h3>
          <p className="text-xs text-muted-foreground">Document URL and notes</p>
        </div>

        <Input
          label="Lease Document URL"
          name="lease_document_url"
          value={values.lease_document_url}
          onChange={handleChange}
          placeholder="https://..."
        />

        <div>
          <label className="text-sm font-medium text-muted-foreground mb-2 block">
            Notes
          </label>
          <textarea
            name="notes"
            value={values.notes}
            onChange={handleChange}
            rows={3}
            className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="Additional notes about the lease..."
          />
        </div>
      </div>

      {/* Error Display */}
      {errors.submit && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
          {errors.submit}
        </div>
      )}

      {/* Form Actions */}
      <div className="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 pt-4">
        <Button type="button" variant="ghost" onClick={onClose} className="mt-2 sm:mt-0">
          Cancel
        </Button>
        <Button type="submit" variant="primary" loading={loading}>
          {isEditing ? 'Update Lease' : 'Create Lease'}
        </Button>
      </div>
    </form>
  )
}

export default LeaseForm