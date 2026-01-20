import React from 'react'
import { Link } from 'react-router-dom'
import {
  Breadcrumb as UIBreadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '../ui/breadcrumb'
import { useBreadcrumbs } from '../../hooks/useBreadcrumbs'

interface BreadcrumbProps {
  customItems?: Array<{
    label: string
    href?: string
    isCurrentPage?: boolean
  }>
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ customItems }) => {
  const defaultBreadcrumbs = useBreadcrumbs()
  const breadcrumbs = customItems || defaultBreadcrumbs

  if (breadcrumbs.length <= 1) {
    return null // Don't show breadcrumbs if we're only on the home page
  }

  return (
    <UIBreadcrumb>
      <BreadcrumbList>
        {breadcrumbs.map((item, index) => (
          <React.Fragment key={index}>
            <BreadcrumbItem>
              {item.isCurrentPage ? (
                <BreadcrumbPage>{item.label}</BreadcrumbPage>
              ) : item.href ? (
                <BreadcrumbLink asChild>
                  <Link to={item.href}>{item.label}</Link>
                </BreadcrumbLink>
              ) : (
                <span className='text-muted-foreground'>{item.label}</span>
              )}
            </BreadcrumbItem>
            {index < breadcrumbs.length - 1 && <BreadcrumbSeparator />}
          </React.Fragment>
        ))}
      </BreadcrumbList>
    </UIBreadcrumb>
  )
}
