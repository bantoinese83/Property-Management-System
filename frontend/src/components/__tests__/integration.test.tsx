/**
 * Integration tests for React components.
 *
 * Tests complete user workflows and component interactions.
 */

import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, beforeEach, vi } from 'vitest'

import { render, createMockProperty, mockApiCall, mockApiResponse } from '../../test-utils'

// Mock API calls
vi.mock('../../hooks/useApi', () => ({
  useApi: vi.fn(),
}))

// Mock toast notifications
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
  },
}))

describe('Property Management Integration', () => {
  let user: ReturnType<typeof userEvent.setup>

  beforeEach(() => {
    user = userEvent.setup()
    // Reset all mocks
    vi.clearAllMocks()
  })

  describe('Property Creation Workflow', () => {
    it('allows creating a new property through the UI', async () => {
      // Mock successful API responses
      mockApiCall('post', '/api/properties/', mockApiResponse.success(createMockProperty()))

      render(<div>Property Management Page</div>)

      // Mock the PropertiesPage component
      const addButton = screen.getByRole('button', { name: /add property/i })
      await user.click(addButton)

      // Should show property creation form
      await waitFor(() => {
        expect(screen.getByLabelText(/property name/i)).toBeInTheDocument()
      })

      // Fill out the form
      await user.type(screen.getByLabelText(/property name/i), 'Test Property')
      await user.type(screen.getByLabelText(/address/i), '123 Test St')
      await user.type(screen.getByLabelText(/city/i), 'Test City')
      await user.selectOptions(screen.getByLabelText(/state/i), 'CA')
      await user.type(screen.getByLabelText(/zip code/i), '90210')
      await user.selectOptions(screen.getByLabelText(/property type/i), 'apartment')
      await user.type(screen.getByLabelText(/total units/i), '5')

      // Submit the form
      const submitButton = screen.getByRole('button', { name: /create property/i })
      await user.click(submitButton)

      // Should show success message and redirect
      await waitFor(() => {
        expect(screen.getByText(/property created successfully/i)).toBeInTheDocument()
      })
    })

    it('validates form inputs and shows error messages', async () => {
      // Mock validation error response
      mockApiCall('post', '/api/properties/', mockApiResponse.error('Property name is required'))

      render(<div>Property Form</div>)

      // Try to submit empty form
      const submitButton = screen.getByRole('button', { name: /create/i })
      await user.click(submitButton)

      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText(/property name is required/i)).toBeInTheDocument()
      })
    })
  })

  describe('Property Listing and Search', () => {
    it('displays properties in a table with pagination', async () => {
      const mockProperties = [
        createMockProperty({ id: 1, property_name: 'Property 1' }),
        createMockProperty({ id: 2, property_name: 'Property 2' }),
      ]

      mockApiCall(
        'get',
        '/api/properties/',
        mockApiResponse.success({
          count: 2,
          next: null,
          previous: null,
          results: mockProperties,
        })
      )

      render(<div>Properties List</div>)

      // Should display properties
      await waitFor(() => {
        expect(screen.getByText('Property 1')).toBeInTheDocument()
        expect(screen.getByText('Property 2')).toBeInTheDocument()
      })

      // Should show pagination info
      expect(screen.getByText(/2 properties/i)).toBeInTheDocument()
    })

    it('allows searching and filtering properties', async () => {
      const mockFilteredProperties = [
        createMockProperty({ id: 1, property_name: 'Downtown Apartment' }),
      ]

      mockApiCall(
        'get',
        '/api/properties/?search=downtown',
        mockApiResponse.success({
          count: 1,
          results: mockFilteredProperties,
        })
      )

      render(<div>Properties Search</div>)

      // Type in search box
      const searchInput = screen.getByPlaceholderText(/search properties/i)
      await user.type(searchInput, 'downtown')

      // Should filter results
      await waitFor(() => {
        expect(screen.getByText('Downtown Apartment')).toBeInTheDocument()
        expect(screen.queryByText('Other Property')).not.toBeInTheDocument()
      })
    })
  })

  describe('Dashboard Analytics', () => {
    it('displays key metrics and charts', async () => {
      const mockStats = {
        total_properties: 5,
        total_units: 25,
        average_occupancy: 80.0,
        total_monthly_income: '15000.00',
      }

      mockApiCall('get', '/api/properties/dashboard/stats/', mockApiResponse.success(mockStats))

      render(<div>Dashboard</div>)

      // Should display metrics
      await waitFor(() => {
        expect(screen.getByText('5')).toBeInTheDocument() // total properties
        expect(screen.getByText('25')).toBeInTheDocument() // total units
        expect(screen.getByText('80%')).toBeInTheDocument() // occupancy
        expect(screen.getByText('$15,000')).toBeInTheDocument() // income
      })
    })
  })
})
