import React, { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { API_ENDPOINTS } from '../api/endpoints'
import type { FinancialTransaction } from '../types/models'
import { Button } from '../components/common/Button'
import { Card } from '../components/common/Card'
import { LoadingSpinner, ErrorMessage, LoadingOverlay } from '../components/common'
import { Badge } from '../components/common/Badge'
import { Plus, TrendingUp, TrendingDown, DollarSign, Calendar } from 'lucide-react'
import '../styles/pages/AccountingPage.css'

interface AccountingResponse {
  results: FinancialTransaction[]
  count: number
  next?: string
  previous?: string
}

const AccountingPage: React.FC = () => {
  const [filters, setFilters] = useState({
    transaction_type: '',
    category: '',
    date_from: '',
    date_to: '',
  })

  const { data, loading, error } = useApi<AccountingResponse>(
    `${API_ENDPOINTS.ACCOUNTING.TRANSACTIONS.LIST}?transaction_type=${filters.transaction_type}&category=${filters.category}&date_from=${filters.date_from}&date_to=${filters.date_to}`
  )

  const transactions = data?.results || []

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
      <div className='flex h-[80vh] items-center justify-center'>
        <LoadingSpinner size='lg' />
      </div>
    )
  }

  if (error) {
    return (
      <div className='flex h-[80vh] items-center justify-center'>
        <ErrorMessage message={error.message} title='Failed to load accounting data' />
      </div>
    )
  }

  return (
    <div className='accounting-page'>
      <div className='accounting-header'>
        <div className='flex justify-between items-center'>
          <div>
            <h1>Accounting</h1>
            <p>Track financial transactions and manage property finances</p>
          </div>
          <Button variant='primary' className='flex items-center gap-2'>
            <Plus className='h-4 w-4' />
            Add Transaction
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className='accounting-summary'>
        <div className='summary-grid'>
          <Card className='summary-card'>
            <div className='summary-content'>
              <div className='summary-icon income'>
                <TrendingUp className='h-6 w-6' />
              </div>
              <div className='summary-info'>
                <p className='summary-label'>Total Income</p>
                <p className='summary-value income'>{formatCurrency(summary.total_income)}</p>
              </div>
            </div>
          </Card>

          <Card className='summary-card'>
            <div className='summary-content'>
              <div className='summary-icon expense'>
                <TrendingDown className='h-6 w-6' />
              </div>
              <div className='summary-info'>
                <p className='summary-label'>Total Expenses</p>
                <p className='summary-value expense'>{formatCurrency(summary.total_expenses)}</p>
              </div>
            </div>
          </Card>

          <Card className='summary-card'>
            <div className='summary-content'>
              <div className='summary-icon profit'>
                <DollarSign className='h-6 w-6' />
              </div>
              <div className='summary-info'>
                <p className='summary-label'>Net Profit</p>
                <p
                  className={`summary-value ${summaryWithProfit.net_profit >= 0 ? 'profit' : 'loss'}`}
                >
                  {formatCurrency(summaryWithProfit.net_profit)}
                </p>
              </div>
            </div>
          </Card>

          <Card className='summary-card'>
            <div className='summary-content'>
              <div className='summary-icon count'>
                <Calendar className='h-6 w-6' />
              </div>
              <div className='summary-info'>
                <p className='summary-label'>Transactions</p>
                <p className='summary-value count'>{summary.transaction_count}</p>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Filters */}
      <div className='accounting-filters'>
        <Card>
          <div className='filters-content'>
            <h3>Filters</h3>
            <div className='filters-grid'>
              <div className='filter-group'>
                <label htmlFor='transaction_type'>Type</label>
                <select
                  id='transaction_type'
                  value={filters.transaction_type}
                  onChange={e => setFilters({ ...filters, transaction_type: e.target.value })}
                  className='filter-select'
                >
                  <option value=''>All Types</option>
                  <option value='income'>Income</option>
                  <option value='expense'>Expense</option>
                </select>
              </div>

              <div className='filter-group'>
                <label htmlFor='category'>Category</label>
                <select
                  id='category'
                  value={filters.category}
                  onChange={e => setFilters({ ...filters, category: e.target.value })}
                  className='filter-select'
                >
                  <option value=''>All Categories</option>
                  <option value='rent'>Rent Income</option>
                  <option value='maintenance'>Maintenance</option>
                  <option value='utilities'>Utilities</option>
                  <option value='insurance'>Insurance</option>
                  <option value='property_tax'>Property Tax</option>
                </select>
              </div>

              <div className='filter-group'>
                <label htmlFor='date_from'>From Date</label>
                <input
                  type='date'
                  id='date_from'
                  value={filters.date_from}
                  onChange={e => setFilters({ ...filters, date_from: e.target.value })}
                  className='filter-input'
                />
              </div>

              <div className='filter-group'>
                <label htmlFor='date_to'>To Date</label>
                <input
                  type='date'
                  id='date_to'
                  value={filters.date_to}
                  onChange={e => setFilters({ ...filters, date_to: e.target.value })}
                  className='filter-input'
                />
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Transactions List */}
      <LoadingOverlay isLoading={loading}>
        <Card>
          <div className='transactions-header'>
            <h3>Transactions</h3>
          </div>

          <div className='transactions-list'>
            {transactions.length === 0 ? (
              <div className='no-transactions'>
                <p>No transactions found matching your filters.</p>
              </div>
            ) : (
              transactions.map(transaction => (
                <div key={transaction.id} className='transaction-item'>
                  <div className='transaction-main'>
                    <div className='transaction-icon'>
                      {getTransactionIcon(transaction.transaction_type)}
                    </div>
                    <div className='transaction-info'>
                      <div className='transaction-title'>
                        <h4>{transaction.description}</h4>
                        <Badge variant={getTransactionTypeVariant(transaction.transaction_type)}>
                          {transaction.transaction_type.toUpperCase()}
                        </Badge>
                      </div>
                      <div className='transaction-meta'>
                        <span className='transaction-category'>{transaction.category_display}</span>
                        <span className='transaction-date'>
                          {new Date(transaction.transaction_date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className='transaction-amount'>
                    <span className={`amount ${transaction.transaction_type}`}>
                      {transaction.transaction_type === 'income' ? '+' : '-'}
                      {formatCurrency(transaction.amount)}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </LoadingOverlay>
    </div>
  )
}

export default AccountingPage
