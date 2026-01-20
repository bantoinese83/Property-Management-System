import * as React from "react"
import {
  BarChartIcon,
  ClipboardListIcon,
  FileTextIcon,
  FolderIcon,
  LayoutDashboardIcon,
  SettingsIcon,
  UsersIcon,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

// Property Management Navigation Data
const data = {
  user: {
    name: "Property Manager",
    email: "manager@propertyco.com",
    avatar: "/avatars/manager.jpg",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: LayoutDashboardIcon,
    },
    {
      title: "Properties",
      url: "/properties",
      icon: FolderIcon,
    },
    {
      title: "Tenants",
      url: "/tenants",
      icon: UsersIcon,
    },
    {
      title: "Leases",
      url: "/leases",
      icon: FileTextIcon,
    },
    {
      title: "Payments",
      url: "/payments",
      icon: BarChartIcon,
    },
    {
      title: "Maintenance",
      url: "/maintenance",
      icon: SettingsIcon,
    },
    {
      title: "Accounting",
      url: "/accounting",
      icon: ClipboardListIcon,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-1.5"
            >
              <a href="/dashboard">
                <LayoutDashboardIcon className="h-5 w-5" />
                <span className="text-base font-semibold">Property Management</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  )
}
