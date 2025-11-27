import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useOrganization } from '@/contexts/OrganizationContext';
import { cn } from '@/lib/utils';
import { SearchableSelect } from '@/components/ui/SearchableSelect';
import {
  Shield,
  LayoutDashboard,
  Building2,
  MapPin,
  Users,
  FileText,
  Lock,
  Settings as SettingsIcon,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Wrench,
  Network,
  GitBranch,
  Trash2,
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const { logout } = useAuth();
  const { selectedOrg, setSelectedOrg, organizations, loading } = useOrganization();
  const navigate = useNavigate();
  const [activeItem, setActiveItem] = useState('dashboard');

  const handleOrgChange = (orgId: string) => {
    if (orgId) {
      const org = organizations.find((o) => o.id.toString() === orgId);
      setSelectedOrg(org || null);
    } else {
      setSelectedOrg(null);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
    { id: 'organizations', label: 'Organizations', icon: Building2, path: '/organizations' },
    { id: 'locations', label: 'Locations', icon: MapPin, path: '/locations' },
    { id: 'contacts', label: 'Contacts', icon: Users, path: '/contacts' },
    { id: 'documentation', label: 'Documentation', icon: FileText, path: '/documentations' },
    { id: 'endpoints', label: 'Endpoints', icon: Network, path: '/endpoints' },
    { id: 'diagram', label: 'Diagram', icon: GitBranch, path: '/diagram' },
    { id: 'passwords', label: 'Passwords', icon: Lock, path: '/passwords' },
    { id: 'configurations', label: 'Configurations', icon: Wrench, path: '/configurations' },
    { id: 'deleted-items', label: 'Deleted Items', icon: Trash2, path: '/deleted-items' },
    { id: 'settings', label: 'Settings', icon: SettingsIcon, path: '/settings' },
  ];

  return (
    <div
      className={cn(
        'bg-card border-r border-border h-screen flex flex-col transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div className={cn('flex items-center gap-3', collapsed && 'justify-center')}>
          <div className="bg-primary/10 p-2 rounded-lg border border-primary/20">
            <Shield className="h-5 w-5 text-primary" />
          </div>
          {!collapsed && (
            <div>
              <h2 className="font-bold text-lg">TechVault</h2>
            </div>
          )}
        </div>
        <button
          onClick={onToggle}
          className={cn(
            'p-1 hover:bg-accent rounded-md transition-colors',
            collapsed && 'absolute right-2'
          )}
        >
          {collapsed ? (
            <ChevronRight className="h-5 w-5" />
          ) : (
            <ChevronLeft className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Organization Selector */}
      {!collapsed && (
        <div className="px-4 py-3 border-b border-border">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">
            Organization
          </label>
          {loading ? (
            <div className="text-sm text-muted-foreground">Loading...</div>
          ) : (
            <SearchableSelect
              options={organizations.map((org) => ({
                value: org.id.toString(),
                label: org.name,
              }))}
              value={selectedOrg?.id.toString() || ''}
              onChange={handleOrgChange}
              placeholder="Select Organization"
            />
          )}
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-2 overflow-y-auto">
        <ul className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeItem === item.id;

            return (
              <li key={item.id}>
                <Link
                  to={item.path}
                  onClick={() => setActiveItem(item.id)}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-md transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-accent hover:text-accent-foreground',
                    collapsed && 'justify-center'
                  )}
                  title={collapsed ? item.label : undefined}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  {!collapsed && <span>{item.label}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Logout */}
      <div className="p-2 border-t border-border">
        <button
          onClick={handleLogout}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2 rounded-md transition-colors hover:bg-destructive hover:text-destructive-foreground',
            collapsed && 'justify-center'
          )}
          title={collapsed ? 'Logout' : undefined}
        >
          <LogOut className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
