/**
 * Utility functions for exporting data to CSV format
 */

export interface ExportColumn {
  key: string
  label: string
  formatter?: (value: unknown) => unknown
}

export const exportToCSV = (data: Record<string, unknown>[], columns: ExportColumn[], filename: string) => {
  // Create CSV header
  const headers = columns.map(col => col.label).join(',')

  // Create CSV rows
  const rows = data.map(item =>
    columns
      .map(col => {
        const value = item[col.key]
        const formatted = col.formatter ? col.formatter(value) : value
        // Escape commas and quotes in CSV
        const stringValue = String(formatted || '')
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`
        }
        return stringValue
      })
      .join(',')
  )

  // Combine header and rows
  const csvContent = [headers, ...rows].join('\n')

  // Create and download file
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Formatters for common data types
export const formatters = {
  currency: (value: number | string) => {
    const num = typeof value === 'string' ? parseFloat(value) : value
    return isNaN(num) ? '$0.00' : `$${num.toFixed(2)}`
  },

  date: (value: string) => {
    if (!value) return ''
    try {
      return new Date(value).toLocaleDateString()
    } catch {
      return value
    }
  },

  boolean: (value: boolean) => (value ? 'Yes' : 'No'),

  capitalize: (value: string) => {
    if (!value) return ''
    return value.charAt(0).toUpperCase() + value.slice(1).toLowerCase()
  },

  replaceUnderscore: (value: string) => {
    if (!value) return ''
    return value.replace(/_/g, ' ')
  },
}

// Predefined column configurations for different entities
export const entityColumns = {
  properties: [
    { key: 'property_name', label: 'Property Name' },
    { key: 'address', label: 'Address' },
    { key: 'city', label: 'City' },
    { key: 'state', label: 'State' },
    { key: 'zip_code', label: 'ZIP Code' },
    { key: 'property_type', label: 'Property Type', formatter: formatters.replaceUnderscore },
    { key: 'total_units', label: 'Total Units' },
    {
      key: 'occupancy_rate',
      label: 'Occupancy Rate (%)',
      formatter: (value: number) => `${value}%`,
    },
    { key: 'monthly_income', label: 'Monthly Income', formatter: formatters.currency },
    { key: 'is_active', label: 'Active', formatter: formatters.boolean },
    { key: 'created_at', label: 'Created Date', formatter: formatters.date },
  ],

  tenants: [
    { key: 'first_name', label: 'First Name' },
    { key: 'last_name', label: 'Last Name' },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Phone' },
    { key: 'address', label: 'Address' },
    { key: 'city', label: 'City' },
    { key: 'state', label: 'State' },
    { key: 'zip_code', label: 'ZIP Code' },
    { key: 'is_active', label: 'Active', formatter: formatters.boolean },
    { key: 'active_lease_count', label: 'Active Leases' },
    { key: 'monthly_rent_total', label: 'Monthly Rent', formatter: formatters.currency },
    { key: 'created_at', label: 'Created Date', formatter: formatters.date },
  ],

  leases: [
    { key: 'property_name', label: 'Property' },
    { key: 'tenant_name', label: 'Tenant' },
    { key: 'lease_start_date', label: 'Start Date', formatter: formatters.date },
    { key: 'lease_end_date', label: 'End Date', formatter: formatters.date },
    { key: 'monthly_rent', label: 'Monthly Rent', formatter: formatters.currency },
    { key: 'deposit_amount', label: 'Security Deposit', formatter: formatters.currency },
    { key: 'status', label: 'Status', formatter: formatters.capitalize },
    { key: 'is_ending_soon', label: 'Ending Soon', formatter: formatters.boolean },
    { key: 'days_remaining', label: 'Days Remaining' },
    { key: 'created_at', label: 'Created Date', formatter: formatters.date },
  ],

  maintenance: [
    { key: 'property_name', label: 'Property' },
    { key: 'tenant_name', label: 'Tenant' },
    { key: 'title', label: 'Title' },
    { key: 'description', label: 'Description' },
    { key: 'priority', label: 'Priority', formatter: formatters.capitalize },
    { key: 'category', label: 'Category', formatter: formatters.capitalize },
    { key: 'status', label: 'Status', formatter: formatters.capitalize },
    { key: 'assigned_to_name', label: 'Assigned To' },
    { key: 'vendor_name', label: 'Vendor' },
    { key: 'estimated_cost', label: 'Estimated Cost', formatter: formatters.currency },
    { key: 'actual_cost', label: 'Actual Cost', formatter: formatters.currency },
    { key: 'requested_date', label: 'Requested Date', formatter: formatters.date },
    { key: 'completed_date', label: 'Completed Date', formatter: formatters.date },
  ],

  payments: [
    { key: 'lease_property_name', label: 'Property' },
    { key: 'lease_tenant_name', label: 'Tenant' },
    { key: 'amount', label: 'Amount', formatter: formatters.currency },
    { key: 'payment_date', label: 'Payment Date', formatter: formatters.date },
    { key: 'due_date', label: 'Due Date', formatter: formatters.date },
    { key: 'payment_method', label: 'Payment Method', formatter: formatters.replaceUnderscore },
    { key: 'status', label: 'Status', formatter: formatters.capitalize },
    { key: 'total_amount', label: 'Total Amount', formatter: formatters.currency },
    { key: 'transaction_id', label: 'Transaction ID' },
    { key: 'processed_at', label: 'Processed Date', formatter: formatters.date },
  ],

  transactions: [
    { key: 'property_name', label: 'Property' },
    { key: 'transaction_type', label: 'Type', formatter: formatters.capitalize },
    { key: 'category', label: 'Category', formatter: formatters.capitalize },
    { key: 'amount', label: 'Amount', formatter: formatters.currency },
    { key: 'description', label: 'Description' },
    { key: 'transaction_date', label: 'Date', formatter: formatters.date },
    { key: 'vendor_name', label: 'Vendor' },
    { key: 'recorded_by_name', label: 'Recorded By' },
    { key: 'created_at', label: 'Created Date', formatter: formatters.date },
  ],
}
