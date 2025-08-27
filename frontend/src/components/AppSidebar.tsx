import { NavLink, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  Wrench, 
  Ticket, 
  ClipboardList, 
  Terminal, 
  LogOut,
  Factory,
  PanelLeftClose
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext"; // Import useAuth

const navItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Maintenance Hub", url: "/maintenance-hub", icon: Wrench },
  { title: "Log New Ticket", url: "/log-ticket", icon: Ticket },
  { title: "Manage Tickets", url: "/manage-tickets", icon: ClipboardList },
  { title: "Operator Terminal", url: "/operator-terminal", icon: Terminal },
];

export function AppSidebar() {
  const location = useLocation();
  const currentPath = location.pathname;
  const { user, logout } = useAuth(); // Use the useAuth hook

  const items = navItems; // Use a single set of navigation items for now
  
  const isActive = (path: string) => currentPath === path;
  
  const getNavCls = ({ isActive }: { isActive: boolean }) =>
    isActive ? "bg-primary/10 text-primary font-medium border-r-2 border-primary" : "hover:bg-muted/50 text-muted-foreground hover:text-foreground";

  const handleLogout = () => {
    logout(); // Call the logout function from AuthContext
  };

  const userName = user ? `${user.first_name} ${user.last_name}` : 'Guest';
  const userRole = user ? user.role : '';

  return (
    <Sidebar collapsible="icon">
      <SidebarContent className="bg-gradient-to-b from-background to-muted/20">
        {/* Header */}
        <div className="p-4 border-b flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-glow rounded-lg flex items-center justify-center">
              <Factory className="w-4 h-4 text-primary-foreground" />
            </div>
            <div className="group-data-[collapsible=icon]:hidden">
              <h2 className="font-semibold text-foreground">Mill Dash</h2>
              <p className="text-xs text-muted-foreground capitalize">{userRole.toLowerCase()}</p>
            </div>
          </div>
          <SidebarTrigger className="group-data-[collapsible=icon]:hidden">
            <PanelLeftClose className="w-4 h-4" />
          </SidebarTrigger>
        </div>

        <SidebarGroup>
          <SidebarGroupLabel className="px-4 py-2 text-xs uppercase tracking-wider text-muted-foreground group-data-[collapsible=icon]:hidden">
            Navigation
          </SidebarGroupLabel>

          <SidebarGroupContent>
            <SidebarMenu className="px-2">
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild className="w-full">
                    <NavLink 
                      to={item.url} 
                      end 
                      className={({ isActive }) => `${getNavCls({ isActive })} flex items-center px-3 py-2 rounded-lg transition-all duration-200`}
                    >
                      <item.icon className="h-4 w-4 shrink-0" />
                      <span className="ml-3 group-data-[collapsible=icon]:hidden">{item.title}</span>
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* User Info & Logout */}
        <div className="mt-auto p-4 border-t">
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-primary">
                  {userName.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <div className="flex-1 min-w-0 group-data-[collapsible=icon]:hidden">
                <p className="text-sm font-medium text-foreground truncate">{userName}</p>
                <p className="text-xs text-muted-foreground capitalize">{userRole.toLowerCase()}</p>
              </div>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleLogout}
              className="w-full justify-start group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-2"
            >
              <LogOut className="w-4 h-4 group-data-[collapsible=icon]:mr-0 mr-2" />
              <span className="group-data-[collapsible=icon]:hidden">Sign Out</span>
            </Button>
          </div>
        </div>
      </SidebarContent>
    </Sidebar>
  );
}