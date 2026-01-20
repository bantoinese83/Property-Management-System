export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/token/',
    REFRESH: '/token/refresh/',
    LOGOUT: '/logout/',
    REGISTER: '/users/',
  },

  // Users
  USERS: {
    ME: '/users/me/',
    PROFILE: (id: number) => `/users/${id}/profile/`,
    LIST: '/users/',
    DETAIL: (id: number) => `/users/${id}/`,
  },

  // Properties
  PROPERTIES: {
    LIST: '/properties/',
    DETAIL: (id: number) => `/properties/${id}/`,
    OCCUPANCY: (id: number) => `/properties/${id}/occupancy_details/`,
    CREATE: '/properties/',
    UPDATE: (id: number) => `/properties/${id}/`,
    DELETE: (id: number) => `/properties/${id}/`,
  },

  // Tenants
  TENANTS: {
    LIST: '/tenants/',
    DETAIL: (id: number) => `/tenants/${id}/`,
    CREATE: '/tenants/',
    UPDATE: (id: number) => `/tenants/${id}/`,
    DELETE: (id: number) => `/tenants/${id}/`,
  },

  // Leases
  LEASES: {
    LIST: '/leases/',
    DETAIL: (id: number) => `/leases/${id}/`,
    CREATE: '/leases/',
    UPDATE: (id: number) => `/leases/${id}/`,
    DELETE: (id: number) => `/leases/${id}/`,
  },

  // Maintenance
  MAINTENANCE: {
    LIST: '/maintenance/',
    DETAIL: (id: number) => `/maintenance/${id}/`,
    CREATE: '/maintenance/',
    UPDATE: (id: number) => `/maintenance/${id}/`,
  },

  // Payments
  PAYMENTS: {
    LIST: '/payments/',
    DETAIL: (id: number) => `/payments/${id}/`,
    CREATE: '/payments/',
    UPDATE: (id: number) => `/payments/${id}/`,
    CREATE_STRIPE_SESSION: (id: number) => `/payments/${id}/create_checkout_session/`,
  },

  // Accounting
  ACCOUNTING: {
    TRANSACTIONS: {
      LIST: '/accounting/transactions/',
      DETAIL: (id: number) => `/accounting/transactions/${id}/`,
      CREATE: '/accounting/transactions/',
      UPDATE: (id: number) => `/accounting/transactions/${id}/`,
      DELETE: (id: number) => `/accounting/transactions/${id}/`,
    },
    PERIODS: {
      LIST: '/accounting/periods/',
      DETAIL: (id: number) => `/accounting/periods/${id}/`,
      CREATE: '/accounting/periods/',
      UPDATE: (id: number) => `/accounting/periods/${id}/`,
      DELETE: (id: number) => `/accounting/periods/${id}/`,
    },
  },

  // Billing
  BILLING: {
    PLANS: '/billing/plans/',
    SUBSCRIPTIONS: '/billing/subscriptions/',
    SUBSCRIPTION_DETAIL: (id: string) => `/billing/subscriptions/${id}/`,
    PAYMENT_METHODS: '/billing/payment-methods/',
    PAYMENT_METHOD_DETAIL: (id: number) => `/billing/payment-methods/${id}/`,
    INVOICES: '/billing/invoices/',
  },

  // Notifications
  NOTIFICATIONS: {
    LIST: '/notifications/',
    DETAIL: (id: number) => `/notifications/${id}/`,
    MARK_READ: (id: number) => `/notifications/${id}/mark_read/`,
    ARCHIVE: (id: number) => `/notifications/${id}/archive/`,
    MARK_ALL_READ: '/notifications/mark_all_read/',
    UNREAD_COUNT: '/notifications/unread_count/',
  },

  NOTIFICATION_PREFERENCES: '/notification-preferences/',

  // Reports
  REPORTS: {
    TEMPLATES: '/reports/templates/',
    GENERATE: '/reports/generate/',
    LIST: '/reports/list/',
  },

  // Audit
  AUDIT: '/audit/',

  // Documents (file uploads)
  DOCUMENTS: {
    LIST: '/documents/',
    DETAIL: (id: number) => `/documents/${id}/`,
    CREATE: '/documents/',
    DELETE: (id: number) => `/documents/${id}/`,
  },

  // Templates (document templates)
  TEMPLATES: {
    LIST: '/templates/',
    DETAIL: (id: number) => `/templates/${id}/`,
    VARIABLES: (id: number) => `/templates/${id}/variables/`,
  },

  // Generated Documents
  GENERATED_DOCUMENTS: {
    LIST: '/templates/generated/',
    DETAIL: (id: number) => `/templates/generated/${id}/`,
    DOWNLOAD: (id: number) => `/templates/generated/${id}/download/`,
    GENERATE: '/templates/generate/',
  },
}
