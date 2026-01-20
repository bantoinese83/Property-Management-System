import React from 'react'
import { type AxiosError } from 'axios'
import { useForm } from '../../hooks/useForm'
import { API_ENDPOINTS } from '../../api/endpoints'
import { type FinancialTransaction } from '../../types/models'
import { Button } from '../common/Button'
import { Input } from '../common/Input'
import client from '../../api/client'

interface TransactionFormProps {
  transaction?: FinancialTransaction
  onClose: () => void
}

type TransactionFormValues = Omit<
  FinancialTransaction,
  'id' | 'recorded_by' | 'recorded_by_name' | 'created_at' | 'updated_at'
>

const TransactionForm: React.FC<TransactionFormProps> = ({ transaction, onClose }) => {
  const isEditing = !!transaction

  const { values, errors, loading, handleChange, handleSubmit, setValue } =
    useForm<TransactionFormValues>({
      initialValues: (transaction as TransactionFormValues) || {
        property_obj: undefined,
        transaction_type: 'expense',
        category: '',
        amount: undefined,
        description: '',
        transaction_date: '',
        lease: undefined,
        maintenance_request: undefined,
        vendor_name: '',
        vendor_invoice_number: '',
        is_recurring: false,
        recurring_frequency: '',
      },
      onSubmit: async formData => {
        try {
          const url = isEditing
            ? API_ENDPOINTS.ACCOUNTING.TRANSACTIONS.DETAIL(transaction!.id)
            : API_ENDPOINTS.ACCOUNTING.TRANSACTIONS.LIST

          const method = isEditing ? 'PUT' : 'POST'

          await client({
            method,
            url,
            data: formData,
          })

          onClose()
        } catch (error) {
          const axiosError = error as AxiosError<{ detail?: string }>
          throw new Error(axiosError.response?.data?.detail || 'Failed to save transaction')
        }
      },
    })

  const incomeCategories = [
    { value: 'rent', label: 'Rent Income' },
    { value: 'late_fees', label: 'Late Fees' },
    { value: 'pet_deposit', label: 'Pet Deposit' },
    { value: 'security_deposit', label: 'Security Deposit' },
    { value: 'other_income', label: 'Other Income' },
  ]

  const expenseCategories = [
    { value: 'maintenance', label: 'Maintenance & Repairs' },
    { value: 'utilities', label: 'Utilities' },
    { value: 'insurance', label: 'Insurance' },
    { value: 'property_tax', label: 'Property Tax' },
    { value: 'management_fees', label: 'Property Management Fees' },
    { value: 'marketing', label: 'Marketing & Advertising' },
    { value: 'legal_fees', label: 'Legal Fees' },
    { value: 'accounting_fees', label: 'Accounting Fees' },
    { value: 'supplies', label: 'Office Supplies' },
    { value: 'other_expenses', label: 'Other Expenses' },
  ]

  const currentCategories = values.transaction_type === 'income' ? incomeCategories : expenseCategories

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Transaction Details */}
      <div className="space-y-3">
        <div>
          <h3 className="text-base font-medium text-foreground">Transaction Details</h3>
          <p className="text-xs text-muted-foreground">Basic transaction information</p>
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

          <div>
            <label className="text-sm font-medium text-muted-foreground mb-2 block">
              Transaction Type
            </label>
            <select
              name="transaction_type"
              value={values.transaction_type}
              onChange={handleChange}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              required
            >
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="text-sm font-medium text-muted-foreground mb-2 block">
              Category
            </label>
            <select
              name="category"
              value={values.category}
              onChange={handleChange}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              required
            >
              <option value="">Select Category</option>
              {currentCategories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <Input
            label="Amount"
            name="amount"
            type="number"
            value={values.amount || ''}
            onChange={handleChange}
            min="0"
            step="0.01"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input
            label="Transaction Date"
            name="transaction_date"
            type="date"
            value={values.transaction_date}
            onChange={handleChange}
            required
          />

          <Input
            label="Lease ID (Optional)"
            name="lease"
            type="number"
            value={values.lease || ''}
            onChange={handleChange}
          />
        </div>
      </div>

      {/* Description & Vendor */}
      <div className="space-y-3">
        <div>
          <h3 className="text-base font-medium text-foreground">Description & Vendor</h3>
          <p className="text-xs text-muted-foreground">Transaction details and vendor information</p>
        </div>

        <Input
          label="Description"
          name="description"
          value={values.description}
          onChange={handleChange}
          required
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Input
            label="Vendor Name"
            name="vendor_name"
            value={values.vendor_name}
            onChange={handleChange}
          />

          <Input
            label="Vendor Invoice Number"
            name="vendor_invoice_number"
            value={values.vendor_invoice_number}
            onChange={handleChange}
          />
        </div>
      </div>

      {/* Recurring Settings */}
      <div className="space-y-3">
        <div>
          <h3 className="text-base font-medium text-foreground">Recurring Settings</h3>
          <p className="text-xs text-muted-foreground">Configure recurring transactions</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="flex items-center space-x-2 pt-6">
            <input
              type="checkbox"
              id="is_recurring"
              name="is_recurring"
              checked={values.is_recurring}
              onChange={e => setValue('is_recurring', e.target.checked)}
              className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            />
            <label htmlFor="is_recurring" className="text-sm font-medium text-foreground">
              This is a recurring transaction
            </label>
          </div>

          {values.is_recurring && (
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Frequency
              </label>
              <select
                name="recurring_frequency"
                value={values.recurring_frequency}
                onChange={handleChange}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="">Select Frequency</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
          )}
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
          {isEditing ? 'Update Transaction' : 'Create Transaction'}
        </Button>
      </div>
    </form>
  )
}

export default TransactionForm