// User-friendly error message mapping
// Transforms technical errors into clear, actionable messages

export interface ErrorMapping {
  [key: string]: string
}

// HTTP Status Code Mappings
export const HTTP_ERROR_MESSAGES: ErrorMapping = {
  400: 'Please check your information and try again.',
  401: 'Your session has expired. Please sign in again.',
  403: 'You don\'t have permission to perform this action.',
  404: 'The item you\'re looking for doesn\'t exist.',
  409: 'This item has already been updated by someone else.',
  422: 'Please check your information - some details are invalid.',
  429: 'You\'re making requests too quickly. Please wait a moment.',
  500: 'Something went wrong on our end. Please try again.',
  502: 'Service is temporarily unavailable. Please try again.',
  503: 'Service is temporarily unavailable. Please try again.',
  504: 'Request timed out. Please check your connection and try again.',
}

// Field-specific error mappings
export const FIELD_ERROR_MESSAGES: ErrorMapping = {
  // Authentication
  'username': 'Please enter a valid username.',
  'password': 'Password must be at least 8 characters long.',
  'email': 'Please enter a valid email address.',
  'non_field_errors': 'Please check your information and try again.',

  // Property fields
  'property_name': 'Please enter a property name.',
  'address': 'Please enter a valid address.',
  'city': 'Please enter a city name.',
  'state': 'Please enter a valid state.',
  'zip_code': 'Please enter a valid ZIP code (e.g., 12345 or 12345-6789).',
  'total_units': 'Number of units must be at least 1.',
  'year_built': 'Please enter a valid year between 1800 and present.',
  'square_footage': 'Square footage must be a positive number.',
  'bedrooms': 'Number of bedrooms must be between 0 and 50.',
  'bathrooms': 'Bathrooms must be between 0 and 20.',
  'purchase_price': 'Purchase price cannot be negative.',
  'annual_property_tax': 'Property tax cannot be negative.',
  'insurance_cost': 'Insurance cost cannot be negative.',

  // Lease fields
  'lease_start_date': 'Please enter a valid start date.',
  'lease_end_date': 'End date must be after the start date.',
  'monthly_rent': 'Monthly rent must be a positive amount.',
  'deposit_amount': 'Deposit cannot be negative.',
  'pet_deposit': 'Pet deposit cannot be negative.',
  'late_fee': 'Late fee cannot be negative.',

  // Tenant fields
  'first_name': 'Please enter a first name.',
  'last_name': 'Please enter a last name.',
  'phone': 'Please enter a valid phone number.',

  // General validations
  'required': 'This field is required.',
  'invalid': 'Please enter valid information.',
  'unique': 'This value is already in use.',
  'max_length': 'This text is too long.',
  'min_value': 'This value is too small.',
  'max_value': 'This value is too large.',
}

// Network and API error mappings
export const NETWORK_ERROR_MESSAGES: ErrorMapping = {
  'NETWORK_ERROR': 'Please check your internet connection and try again.',
  'TIMEOUT': 'Request timed out. Please try again.',
  'CORS_ERROR': 'Connection issue. Please refresh the page.',
  'SERVER_ERROR': 'Server is temporarily unavailable. Please try again in a few minutes.',
  'MAINTENANCE': 'System is under maintenance. Please check back soon.',
}

// Action-specific error messages
export const ACTION_ERROR_MESSAGES: ErrorMapping = {
  'CREATE_PROPERTY': 'Unable to create property. Please check your information.',
  'UPDATE_PROPERTY': 'Unable to update property. Please try again.',
  'DELETE_PROPERTY': 'Unable to delete property. Please try again.',
  'CREATE_LEASE': 'Unable to create lease. Please check the dates and information.',
  'UPDATE_LEASE': 'Unable to update lease. Please try again.',
  'CREATE_TENANT': 'Unable to create tenant. Please check the information.',
  'UPDATE_TENANT': 'Unable to update tenant. Please try again.',
  'PROCESS_PAYMENT': 'Unable to process payment. Please check your payment information.',
  'UPLOAD_DOCUMENT': 'Unable to upload document. Please check the file and try again.',
  'SEND_EMAIL': 'Unable to send email. Please try again.',
}

/**
 * Get user-friendly error message from error object
 */
export function getUserFriendlyError(error: any): string {
  // Handle HTTP status codes
  if (error?.response?.status) {
    const statusMessage = HTTP_ERROR_MESSAGES[error.response.status]
    if (statusMessage) return statusMessage
  }

  // Handle field-specific errors
  if (error?.response?.data) {
    const data = error.response.data

    // Check for field errors
    for (const [field, messages] of Object.entries(data)) {
      if (Array.isArray(messages) && messages.length > 0) {
        const fieldMessage = FIELD_ERROR_MESSAGES[field]
        if (fieldMessage) return fieldMessage
        // Return the first message if no mapping exists
        return String(messages[0])
      }
    }

    // Check for non-field errors
    if (data.detail) return data.detail
    if (data.message) return data.message
    if (data.error) return data.error
  }

  // Handle network errors
  if (!error?.response) {
    if (error?.code === 'NETWORK_ERROR') return NETWORK_ERROR_MESSAGES.NETWORK_ERROR
    if (error?.code === 'TIMEOUT') return NETWORK_ERROR_MESSAGES.TIMEOUT
    return 'Connection issue. Please check your internet and try again.'
  }

  // Fallback to generic message
  return 'Something went wrong. Please try again.'
}

/**
 * Get field-specific error message
 */
export function getFieldError(fieldName: string, error: any): string {
  if (error?.response?.data?.[fieldName]) {
    const messages = error.response.data[fieldName]
    if (Array.isArray(messages) && messages.length > 0) {
      return String(messages[0])
    }
  }

  return FIELD_ERROR_MESSAGES[fieldName] || 'Please enter valid information.'
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: any): boolean {
  const status = error?.response?.status
  return status >= 500 || status === 429 || !error?.response
}