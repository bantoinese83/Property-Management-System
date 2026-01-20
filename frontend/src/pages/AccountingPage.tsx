import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import type { FinancialTransaction } from '../types/models'
import { AppSidebar } from '../components/app-sidebar'
import { SiteHeader } from '../components/site-header'
import { SidebarInset, SidebarProvider } from '../components/ui/sidebar'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { Modal } from '../components/common/Modal'
import { Input } from '../components/common/Input'
import { LoadingSpinner, ErrorMessage } from '../components/common'
import { Badge } from '../components/common/Badge'
import {
  Plus,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calculator,
  FileText,
  Download,
} from 'lucide-react'
import { exportToCSV, entityColumns, type ExportColumn } from '../utils/export'
import { toast } from 'sonner'
import TransactionForm from '../components/accounting/TransactionForm'

interface AccountingResponse {
  results: FinancialTransaction[]
  count: number
  next?: string
  previous?: string
}

const AccountingPage: React.FC = () => {
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingTransaction, setEditingTransaction] = useState<FinancialTransaction | null>(null)
  const [filters, setFilters] = useState({
    transaction_type: '',
    category: '',
    date_from: '',
    date_to: '',
  })

  const { data, loading, error, refetch } = useApi<AccountingResponse>(
    `${API_ENDPOINTS.ACCOUNTING.TRANSACTIONS.LIST}?transaction_type=${filters.transaction_type}&category=${filters.category}&date_from=${filters.date_from}&date_to=${filters.date_to}`
  )

  const transactions = data?.results || []

  const handleAddTransaction = () => {
    setShowAddModal(true)
  }

  const handleCloseModal = () => {
    setShowAddModal(false)
    setEditingTransaction(null)
    refetch() // Refresh the list
  }

  const handleExportData = () => {
    if (transactions.length === 0) {
      toast.error('No data to export', {
        description: 'There are no transactions to export.',
      })
      return
    }

    try {
      exportToCSV(transactions as unknown as Record<string, unknown>[], entityColumns.transactions as ExportColumn[], 'accounting_transactions')
      toast.success('Export successful', {
        description: 'Accounting transactions data has been exported to CSV.',
      })
    } catch (error) {
      console.error('Export failed:', error)
      toast.error('Export failed', {
        description: 'An error occurred while exporting data.',
      })
    }
  }

  const formatCurrency = (amount: string | number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(typeof amount === 'string' ? parseFloat(amount) : amount)
  }

  const getTransactionTypeVariant = (type: string) => {
    return type === 'income' ? 'success' : 'danger'
  }

  const getTransactionIcon = (type: string) => {
    return type === 'income' ? (
      <TrendingUp className='h-4 w-4' />
    ) : (
      <TrendingDown className='h-4 w-4' />
    )
  }

  const summary = transactions.reduce(
    (acc, transaction) => {
      const amount = parseFloat(transaction.amount.toString())
      if (transaction.transaction_type === 'income') {
        acc.total_income += amount
      } else {
        acc.total_expenses += amount
      }
      acc.transaction_count++
      return acc
    },
    { total_income: 0, total_expenses: 0, transaction_count: 0 }
  )

  const summaryWithProfit = {
    ...summary,
    net_profit: summary.total_income - summary.total_expenses,
  }

  if (loading && !transactions.length) {
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
            <div className='flex items-center justify-between'>
              <div>
                <h1 className='text-3xl font-bold tracking-tight'>Accounting</h1>
                <p className='text-muted-foreground'>
                  Track financial transactions and manage property finances
                </p>
              </div>
            </div>
            <div className='flex flex-1 items-center justify-center'>
              <LoadingSpinner size='lg' />
            </div>
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
          <div className='flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6'>
            <div className='flex items-center justify-between'>
              <div>
                <h1 className='text-3xl font-bold tracking-tight'>Accounting</h1>
                <p className='text-muted-foreground'>
                  Track financial transactions and manage property finances
                </p>
              </div>
            </div>
            <div className='flex flex-1 items-center justify-center'>
              <ErrorMessage message={error.message} title='Failed to load accounting data' />
            </div>
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
              <h1 className='text-3xl font-bold tracking-tight'>Accounting</h1>
              <p className='text-muted-foreground'>
                Track financial transactions and manage property finances
              </p>
            </div>
            <div className='flex gap-2'>
              <Button variant='outline' onClick={handleExportData}>
                <Download className='h-4 w-4 mr-2' />
                Export CSV
              </Button>
              <Button
                variant='primary'
                onClick={handleAddTransaction}
                className='flex items-center gap-2'
              >
                <Plus className='h-4 w-4' />
                Add Transaction
              </Button>
            </div>
          </div>

          {/* Stats Cards */}
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-4'>
            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Total Income</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl text-green-600'>
                    {formatCurrency(summary.total_income)}
                  </p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-green-100'>
                  <TrendingUp className='h-5 w-5 text-green-600' />
                </div>
              </div>
            </div>

            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Total Expenses</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl text-red-600'>
                    {formatCurrency(summary.total_expenses)}
                  </p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-red-100'>
                  <TrendingDown className='h-5 w-5 text-red-600' />
                </div>
              </div>
            </div>

            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Net Profit</p>
                  <p
                    className={`text-2xl font-bold tabular-nums lg:text-3xl ${
                      summaryWithProfit.net_profit >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {formatCurrency(summaryWithProfit.net_profit)}
                  </p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <DollarSign className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>

            <div className='rounded-lg border bg-card p-6 shadow-sm'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>Transactions</p>
                  <p className='text-2xl font-bold tabular-nums lg:text-3xl'>
                    {summary.transaction_count}
                  </p>
                </div>
                <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10'>
                  <Calculator className='h-5 w-5 text-primary' />
                </div>
              </div>
            </div>
          </div>

          {/* Filters Section */}
          <div className='flex flex-col gap-4 md:flex-row md:items-end md:justify-between'>
            <div className='flex flex-1 gap-4'>
              <div className='flex-1'>
                <label className='text-sm font-medium text-muted-foreground mb-2 block'>
                  Transaction Type
                </label>
                <select
                  value={filters.transaction_type}
                  onChange={e => setFilters({ ...filters, transaction_type: e.target.value })}
                  className='flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
                >
                  <option value=''>All Types</option>
                  <option value='income'>Income</option>
                  <option value='expense'>Expense</option>
                </select>
              </div>
              <div className='flex-1'>
                <label className='text-sm font-medium text-muted-foreground mb-2 block'>
                  Category
                </label>
                <select
                  value={filters.category}
                  onChange={e => setFilters({ ...filters, category: e.target.value })}
                  className='flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
                >
                  <option value=''>All Categories</option>
                  <option value='rent'>Rent Income</option>
                  <option value='late_fees'>Late Fees</option>
                  <option value='pet_deposit'>Pet Deposit</option>
                  <option value='security_deposit'>Security Deposit</option>
                  <option value='maintenance'>Maintenance & Repairs</option>
                  <option value='utilities'>Utilities</option>
                  <option value='insurance'>Insurance</option>
                  <option value='property_tax'>Property Tax</option>
                  <option value='management_fees'>Property Management Fees</option>
                  <option value='marketing'>Marketing & Advertising</option>
                  <option value='legal_fees'>Legal Fees</option>
                  <option value='accounting_fees'>Accounting Fees</option>
                  <option value='supplies'>Office Supplies</option>
                  <option value='other_expenses'>Other Expenses</option>
                </select>
              </div>
              <div className='flex-1'>
                <label className='text-sm font-medium text-muted-foreground mb-2 block'>
                  From Date
                </label>
                <Input
                  type='date'
                  value={filters.date_from}
                  onChange={e => setFilters({ ...filters, date_from: e.target.value })}
                />
              </div>
              <div className='flex-1'>
                <label className='text-sm font-medium text-muted-foreground mb-2 block'>
                  To Date
                </label>
                <Input
                  type='date'
                  value={filters.date_to}
                  onChange={e => setFilters({ ...filters, date_to: e.target.value })}
                />
              </div>
            </div>
          </div>

          {/* Transactions Grid */}
          <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-3'>
            {transactions.length === 0 ? (
              <div className='col-span-full rounded-lg border border-dashed p-8 text-center'>
                <FileText className='mx-auto h-12 w-12 text-muted-foreground' />
                <h3 className='mt-2 text-sm font-medium'>No transactions found</h3>
                <p className='mt-1 text-sm text-muted-foreground'>
                  Get started by adding your first financial transaction.
                </p>
              </div>
            ) : (
              transactions.map(transaction => (
                <Card key={transaction.id} className='p-6'>
                  <div className='flex items-start justify-between'>
                    <div className='flex items-center gap-3'>
                      <div
                        className={`flex h-10 w-10 items-center justify-center rounded-lg ${
                          transaction.transaction_type === 'income'
                            ? 'bg-green-100 text-green-600'
                            : 'bg-red-100 text-red-600'
                        }`}
                      >
                        {getTransactionIcon(transaction.transaction_type)}
                      </div>
                      <div className='flex-1'>
                        <h3 className='font-semibold text-sm text-foreground truncate'>
                          {transaction.description}
                        </h3>
                        <p className='text-sm text-muted-foreground'>
                          {transaction.category_display}
                        </p>
                      </div>
                    </div>
                    <Badge
                      variant={getTransactionTypeVariant(transaction.transaction_type)}
                      className='text-xs'
                    >
                      {transaction.transaction_type.toUpperCase()}
                    </Badge>
                  </div>

                  <div className='mt-4 space-y-2'>
                    <div className='flex items-center justify-between'>
                      <span className='text-sm text-muted-foreground'>Amount</span>
                      <span
                        className={`font-semibold ${
                          transaction.transaction_type === 'income'
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}
                      >
                        {transaction.transaction_type === 'income' ? '+' : '-'}
                        {formatCurrency(transaction.amount)}
                      </span>
                    </div>
                    <div className='flex items-center justify-between'>
                      <span className='text-sm text-muted-foreground'>Date</span>
                      <span className='text-sm'>
                        {new Date(transaction.transaction_date).toLocaleDateString()}
                      </span>
                    </div>
                    {transaction.vendor_name && (
                      <div className='flex items-center justify-between'>
                        <span className='text-sm text-muted-foreground'>Vendor</span>
                        <span className='text-sm truncate ml-2'>{transaction.vendor_name}</span>
                      </div>
                    )}
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>
      </SidebarInset>

      {/* Add Transaction Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={handleCloseModal}
        title='Add New Transaction'
        size='2xl'
      >
        <TransactionForm onClose={handleCloseModal} />
      </Modal>

      {/* Edit Transaction Modal */}
      <Modal
        isOpen={!!editingTransaction}
        onClose={handleCloseModal}
        title='Edit Transaction'
        size='2xl'
      >
        {editingTransaction && (
          <TransactionForm transaction={editingTransaction} onClose={handleCloseModal} />
        )}
      </Modal>
    </SidebarProvider>
  )
}

export default AccountingPage
