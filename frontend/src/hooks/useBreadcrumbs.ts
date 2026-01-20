import { useLocation } from 'react-router-dom'
import { useMemo } from 'react'

export interface BreadcrumbItem {
  label: string
  href?: string
  isCurrentPage?: boolean
}

const routeLabels: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/properties': 'Properties',
  '/tenants': 'Tenants',
  '/leases': 'Leases',
  '/maintenance': 'Maintenance',
  '/payments': 'Payments',
  '/accounting': 'Accounting',
}

export const useBreadcrumbs = (): BreadcrumbItem[] => {
  const location = useLocation()

  const breadcrumbs = useMemo(() => {
    const pathSegments = location.pathname.split('/').filter(Boolean)
    const breadcrumbs: BreadcrumbItem[] = [{ label: 'Home', href: '/dashboard' }]

    // Build breadcrumbs based on path segments
    let currentPath = ''
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`
      const isLast = index === pathSegments.length - 1
      const label = routeLabels[currentPath] || segment.charAt(0).toUpperCase() + segment.slice(1)

      breadcrumbs.push({
        label,
        href: isLast ? undefined : currentPath,
        isCurrentPage: isLast,
      })
    })

    return breadcrumbs
  }, [location.pathname])

  return breadcrumbs
}
