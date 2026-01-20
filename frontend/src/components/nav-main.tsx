import { useState } from 'react'
import {
  MailIcon,
  PlusCircleIcon,
  type LucideIcon,
  Home,
  Users,
  FileText,
  Wrench,
  DollarSign,
} from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

export function NavMain({
  items,
}: {
  items: {
    title: string
    url: string
    icon?: LucideIcon
  }[]
}) {
  const [isQuickCreateOpen, setIsQuickCreateOpen] = useState(false)
  const navigate = useNavigate()

  const quickCreateItems = [
    {
      title: 'Property',
      url: '/properties',
      icon: Home,
      description: 'Add new property',
    },
    {
      title: 'Tenant',
      url: '/tenants',
      icon: Users,
      description: 'Add new tenant',
    },
    {
      title: 'Lease',
      url: '/leases',
      icon: FileText,
      description: 'Create new lease',
    },
    {
      title: 'Maintenance',
      url: '/maintenance',
      icon: Wrench,
      description: 'Log maintenance request',
    },
    {
      title: 'Payment',
      url: '/payments',
      icon: DollarSign,
      description: 'Record payment',
    },
  ]

  return (
    <SidebarGroup>
      <SidebarGroupContent className='flex flex-col gap-2'>
        <SidebarMenu>
          <SidebarMenuItem className='flex items-center gap-2'>
            <DropdownMenu open={isQuickCreateOpen} onOpenChange={setIsQuickCreateOpen}>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton
                  tooltip='Quick Create'
                  className='min-w-8 bg-primary text-primary-foreground duration-200 ease-linear hover:bg-primary/90 hover:text-primary-foreground active:bg-primary/90 active:text-primary-foreground'
                >
                  <PlusCircleIcon />
                  <span>Quick Create</span>
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent align='start' className='w-56'>
                {quickCreateItems.map(item => (
                  <DropdownMenuItem key={item.title} asChild>
                    <Link
                      to={item.url}
                      className='flex items-center gap-3 cursor-pointer'
                      onClick={() => setIsQuickCreateOpen(false)}
                    >
                      {item.icon && <item.icon className='h-4 w-4' />}
                      <div className='flex flex-col'>
                        <span className='font-medium'>{item.title}</span>
                        <span className='text-xs text-muted-foreground'>{item.description}</span>
                      </div>
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            <Button
              size='icon'
              className='h-9 w-9 shrink-0 group-data-[collapsible=icon]:opacity-0'
              variant='outline'
              onClick={() => navigate('/notifications')}
              title='View Notifications'
            >
              <MailIcon />
              <span className='sr-only'>Inbox</span>
            </Button>
          </SidebarMenuItem>
        </SidebarMenu>
        <SidebarMenu>
          {items.map(item => (
            <SidebarMenuItem key={item.title}>
              <SidebarMenuButton tooltip={item.title} asChild>
                <Link to={item.url}>
                  {item.icon && <item.icon />}
                  <span>{item.title}</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  )
}
