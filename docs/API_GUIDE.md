# Property Management System - API Guide

## Overview

The Property Management System provides a comprehensive REST API for managing rental properties, tenants, leases, payments, and financial reporting. The API follows RESTful conventions and includes OpenAPI documentation.

## Base URL
```
https://yourdomain.com/api/
```

## Authentication

All API requests require authentication using JWT tokens.

### Obtaining a Token
```bash
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Using Tokens
Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Refreshing Tokens
```bash
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "your_refresh_token"
}
```

## Core Resources

### Properties

#### List Properties
```bash
GET /api/properties/
Authorization: Bearer <token>
```

**Query Parameters:**
- `search`: Search in property name, address, city
- `property_type`: Filter by property type
- `is_active`: Filter by active status
- `city`: Filter by city
- `state`: Filter by state
- `page`: Page number for pagination
- `page_size`: Results per page (max 100)

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/properties/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "property_name": "Downtown Luxury Apartment",
      "address": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "zip_code": "10001",
      "property_type": "apartment",
      "total_units": 10,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Create Property
```bash
POST /api/properties/
Authorization: Bearer <token>
Content-Type: application/json

{
  "property_name": "New Property",
  "address": "456 Oak Avenue",
  "city": "Springfield",
  "state": "IL",
  "zip_code": "62701",
  "property_type": "house",
  "total_units": 1,
  "purchase_price": 250000.00,
  "year_built": 2005
}
```

#### Get Property Details
```bash
GET /api/properties/{id}/
Authorization: Bearer <token>
```

#### Update Property
```bash
PUT /api/properties/{id}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "property_name": "Updated Property Name",
  "is_active": false
}
```

### Tenants

#### List Tenants
```bash
GET /api/tenants/
Authorization: Bearer <token>
```

**Query Parameters:**
- `search`: Search in name, email
- `email`: Filter by email

#### Create Tenant
```bash
POST /api/tenants/
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@email.com",
  "phone": "555-0123"
}
```

### Leases

#### List Leases
```bash
GET /api/leases/
Authorization: Bearer <token>
```

**Query Parameters:**
- `property_obj`: Filter by property ID
- `tenant`: Filter by tenant ID
- `status`: Filter by status (draft, active, expired, terminated)
- `lease_end_date_after`: Leases ending after date
- `lease_end_date_before`: Leases ending before date

#### Create Lease
```bash
POST /api/leases/
Authorization: Bearer <token>
Content-Type: application/json

{
  "property_obj": 1,
  "tenant": 1,
  "lease_start_date": "2024-01-01",
  "lease_end_date": "2024-12-31",
  "monthly_rent": 2000.00,
  "deposit_amount": 2000.00,
  "pet_deposit": 500.00
}
```

### Payments

#### List Payments
```bash
GET /api/payments/
Authorization: Bearer <token>
```

**Query Parameters:**
- `lease_obj`: Filter by lease ID
- `status`: Filter by payment status
- `payment_date_after`: Payments after date
- `payment_date_before`: Payments before date
- `due_date_after`: Due after date
- `due_date_before`: Due before date

#### Record Payment
```bash
POST /api/payments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "lease_obj": 1,
  "amount": 2000.00,
  "payment_date": "2024-01-01",
  "due_date": "2024-01-01",
  "payment_method": "bank_transfer",
  "status": "paid"
}
```

### Maintenance

#### List Maintenance Requests
```bash
GET /api/maintenance/
Authorization: Bearer <token>
```

**Query Parameters:**
- `property`: Filter by property ID
- `status`: Filter by status (pending, scheduled, in_progress, completed)
- `priority`: Filter by priority (low, medium, high, urgent)
- `category`: Filter by category (plumbing, electrical, hvac, etc.)

#### Create Maintenance Request
```bash
POST /api/maintenance/
Authorization: Bearer <token>
Content-Type: application/json

{
  "property": 1,
  "title": "Leaky Faucet",
  "description": "Kitchen faucet is leaking water",
  "priority": "medium",
  "category": "plumbing",
  "scheduled_date": "2024-01-15"
}
```

### Financial Transactions

#### List Transactions
```bash
GET /api/accounting/transactions/
Authorization: Bearer <token>
```

**Query Parameters:**
- `property_obj`: Filter by property ID
- `transaction_type`: Filter by type (income, expense)
- `category`: Filter by category
- `transaction_date_after`: After date
- `transaction_date_before`: Before date

#### Create Transaction
```bash
POST /api/accounting/transactions/
Authorization: Bearer <token>
Content-Type: application/json

{
  "property_obj": 1,
  "transaction_type": "income",
  "category": "rent",
  "amount": 2000.00,
  "description": "January 2024 Rent",
  "transaction_date": "2024-01-01"
}
```

## Analytics & Reporting

### Dashboard Statistics
```bash
GET /api/properties/dashboard_stats/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_properties": 5,
  "total_units": 25,
  "average_occupancy": 80.0,
  "total_monthly_income": "15000.00"
}
```

### Dashboard Analytics
```bash
GET /api/properties/dashboard_analytics/
Authorization: Bearer <token>
```

Returns comprehensive analytics including occupancy trends, financial metrics, and maintenance statistics.

## Reports

### Generate Report
```bash
POST /api/reports/generate/
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_id": 1,
  "parameters": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "property_id": 1
  }
}
```

### List Reports
```bash
GET /api/reports/list/
Authorization: Bearer <token>
```

### Get Report Templates
```bash
GET /api/reports/templates/
Authorization: Bearer <token>
```

## Document Management

### List Templates
```bash
GET /api/templates/
Authorization: Bearer <token>
```

### Generate Document
```bash
POST /api/templates/generate/
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_id": 1,
  "variables": {
    "tenant_name": "John Doe",
    "property_address": "123 Main St",
    "monthly_rent": "2000.00",
    "lease_start_date": "2024-01-01",
    "lease_end_date": "2024-12-31"
  },
  "title": "Lease Agreement"
}
```

### List Generated Documents
```bash
GET /api/templates/generated/
Authorization: Bearer <token>
```

### Download Document
```bash
GET /api/templates/generated/{id}/download/
Authorization: Bearer <token>
```

## Audit & Compliance

### List Audit Logs
```bash
GET /api/audit/
Authorization: Bearer <token>
```

**Query Parameters:**
- `user`: Filter by user ID
- `action`: Filter by action type
- `timestamp_after`: After timestamp
- `timestamp_before`: Before timestamp
- `content_type`: Filter by model type

## File Upload

### Upload Document
```bash
POST /api/documents/
Authorization: Bearer <token>
Content-Type: multipart/form-data

# Include file in FormData
file: <uploaded_file>
title: "Lease Document"
description: "Signed lease agreement"
```

## Data Export

### Export Properties
```bash
GET /api/properties/?export=csv
Authorization: Bearer <token>
```

### Export Tenants
```bash
GET /api/tenants/?export=csv
Authorization: Bearer <token>
```

### Export Payments
```bash
GET /api/payments/?export=csv
Authorization: Bearer <token>
```

## Health Checks

### System Health
```bash
GET /health/
```

Returns comprehensive health status of all system components.

### Readiness Check
```bash
GET /ready/
```

Returns 200 if application is ready to serve traffic.

### Metrics
```bash
GET /metrics/
Authorization: Bearer <token>
```

Returns system performance metrics and statistics.

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized
- `403`: Forbidden (permission denied)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include detailed error messages:

```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "not_authenticated"
}
```

Validation errors include field-specific details:

```json
{
  "property_name": ["This field is required."],
  "address": ["This field may not be blank."]
}
```

## Rate Limiting

API endpoints are rate limited to prevent abuse:
- Authenticated requests: 1000/hour
- Anonymous requests: 100/hour
- File uploads: 50/hour

## Pagination

List endpoints support pagination:
- Default page size: 20
- Maximum page size: 100
- Use `page` and `page_size` query parameters

## Filtering & Searching

Most list endpoints support:
- `search`: Full-text search across relevant fields
- `ordering`: Sort by specific fields (use `-` for descending)
- Field-specific filters as documented above

## Webhooks

### Stripe Payment Webhooks
```bash
POST /api/webhooks/stripe/
Content-Type: application/json
X-Stripe-Signature: <signature>

# Webhook payload from Stripe
```

## SDKs & Libraries

### JavaScript/TypeScript Client
```javascript
import { PMSApi } from '@property-mgmt/api-client'

const api = new PMSApi({
  baseURL: 'https://yourdomain.com/api',
  token: 'your_jwt_token'
})

// Example usage
const properties = await api.properties.list()
const newProperty = await api.properties.create(propertyData)
```

### Python Client
```python
from property_mgmt_client import PMSClient

client = PMSClient(
    base_url='https://yourdomain.com/api',
    token='your_jwt_token'
)

# Example usage
properties = client.properties.list()
new_property = client.properties.create(property_data)
```

## Best Practices

### Authentication
- Always use HTTPS in production
- Implement token refresh logic
- Handle token expiration gracefully
- Store tokens securely (httpOnly cookies recommended)

### Error Handling
- Check HTTP status codes
- Parse error responses for user feedback
- Implement retry logic for network errors
- Handle rate limiting appropriately

### Performance
- Use pagination for large datasets
- Implement caching for frequently accessed data
- Use appropriate filtering to reduce payload size
- Batch operations when possible

### Security
- Validate all input data
- Use parameterized queries (handled automatically)
- Implement proper CORS policies
- Keep API tokens secure and rotate regularly

## Support

For API support and questions:
- **Documentation**: Visit `/api/docs/` for interactive documentation
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join community discussions
- **Email**: Contact support@property-mgmt.com

---

*This API guide covers version 1.0.0 of the Property Management System API.*