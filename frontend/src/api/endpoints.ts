export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/token/',
    REFRESH: '/token/refresh/',
    LOGOUT: '/logout/',
    REGISTER: '/users/',
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

  // Documents
  DOCUMENTS: {
    LIST: '/documents/',
    DETAIL: (id: number) => `/documents/${id}/`,
    CREATE: '/documents/',
    DELETE: (id: number) => `/documents/${id}/`,
  },
}
