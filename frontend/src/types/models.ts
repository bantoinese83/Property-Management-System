export interface Property {
  id: number
  owner: number
  owner_name: string
  property_name: string
  description: string
  address: string
  city: string
  state: string
  zip_code: string
  country: string
  latitude?: number
  longitude?: number
  full_address: string
  property_type:
    | 'single_family'
    | 'apartment'
    | 'condo'
    | 'townhouse'
    | 'duplex'
    | 'commercial'
    | 'industrial'
    | 'other'
  total_units: number
  year_built?: number
  square_footage?: number
  bedrooms?: number
  bathrooms?: number
  purchase_price?: number
  purchase_date?: string
  annual_property_tax?: number
  insurance_cost?: number
  is_active: boolean
  is_listed_for_rent: boolean
  occupancy_rate: number
  monthly_income: string
  images: PropertyImage[]
  created_at: string
  updated_at: string
}

export interface PropertyImage {
  id: number
  image: string
  caption: string
  is_primary: boolean
  uploaded_at: string
}

export interface Tenant {
  id: number
  first_name: string
  last_name: string
  full_name: string
  email: string
  phone: string
  date_of_birth?: string
  address: string
  city: string
  state: string
  zip_code: string
  emergency_contact_name: string
  emergency_contact_phone: string
  emergency_contact_relationship: string
  employer_name: string
  employer_phone: string
  annual_income?: number
  previous_landlord_name: string
  previous_landlord_phone: string
  is_active: boolean
  credit_score?: number
  active_lease_count: number
  monthly_rent_total: string
  created_at: string
  updated_at: string
}

export interface Lease {
  id: number
  property: number
  property_name: string
  tenant: number
  tenant_name: string
  lease_start_date: string
  lease_end_date: string
  signed_date?: string
  monthly_rent: number
  deposit_amount?: number
  pet_deposit: number
  late_fee: number
  lease_document_url?: string
  status: 'draft' | 'pending' | 'active' | 'expired' | 'terminated'
  auto_renew: boolean
  renewal_notice_days: number
  notes: string
  days_remaining: number
  is_ending_soon: boolean
  is_expired: boolean
  created_at: string
  updated_at: string
}

export interface MaintenanceRequest {
  id: number
  property: number
  property_name: string
  tenant?: number
  tenant_name?: string
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  category: string
  status: 'open' | 'assigned' | 'in_progress' | 'completed' | 'closed'
  assigned_to?: number
  assigned_to_name?: string
  vendor_name: string
  vendor_phone: string
  vendor_email: string
  estimated_cost?: number
  actual_cost?: number
  requested_date: string
  scheduled_date?: string
  completed_date?: string
  images: string[]
  notes: string
  is_overdue: boolean
  days_since_request: number
  created_at: string
  updated_at: string
}

export interface RentPayment {
  id: number
  lease: number
  lease_property_name: string
  lease_tenant_name: string
  amount: number
  payment_date: string
  due_date: string
  payment_method: 'credit_card' | 'bank_transfer' | 'check' | 'cash' | 'online'
  status: 'pending' | 'paid' | 'overdue' | 'refunded' | 'failed'
  transaction_id?: string
  payment_processor?: string
  late_fee: number
  total_amount: string
  notes: string
  processed_by?: number
  processed_by_name?: string
  processed_at?: string
  is_late: boolean
  created_at: string
  updated_at: string
}

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  user_type: 'admin' | 'manager' | 'owner' | 'tenant'
  phone_number: string
  profile_picture?: string
  date_of_birth?: string
  address: string
  city: string
  state: string
  zip_code: string
  is_verified: boolean
  is_email_verified: boolean
  two_factor_enabled: boolean
  profile?: Record<string, unknown>
  date_joined: string
  last_login?: string
}

export interface Document {
  id: number
  title: string
  description: string
  file: string
  file_type: string
  file_size: number
  content_type: number
  object_id: number
  uploaded_by: number
  uploaded_by_name: string
  created_at: string
  updated_at: string
}

export interface FinancialTransaction {
  id: number
  property: number
  property_name?: string
  transaction_type: 'income' | 'expense'
  category: string
  category_display?: string
  amount: number | string
  description: string
  transaction_date: string
  lease?: number
  lease_tenant_name?: string
  maintenance_request?: number
  maintenance_title?: string
  created_at: string
  updated_at: string
}

export interface AccountingPeriod {
  id: number
  period_name: string
  start_date: string
  end_date: string
  is_closed: boolean
  total_income: number
  total_expenses: number
  net_profit: number
  created_at: string
  updated_at: string
}
