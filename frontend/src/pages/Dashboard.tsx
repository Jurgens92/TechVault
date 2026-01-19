import React, { useEffect, useState, useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { PageHeader } from '@/components/PageHeader';
import { Shield, Building2, MapPin, Users, FileText, Lock, Wrench, TrendingUp, Network } from 'lucide-react';
import { dashboardAPI } from '@/services/core';

interface DashboardStats {
  organizations: number;
  locations: number;
  contacts: number;
  documentations: number;
  passwords: number;
  configurations: number;
  network_devices?: number;
  endpoint_users?: number;
  servers?: number;
  peripherals?: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    organizations: 0,
    locations: 0,
    contacts: 0,
    documentations: 0,
    passwords: 0,
    configurations: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await dashboardAPI.getStats();
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const totalEndpoints = useMemo(() =>
    (stats.network_devices || 0) + (stats.endpoint_users || 0) + (stats.servers || 0) + (stats.peripherals || 0),
    [stats.network_devices, stats.endpoint_users, stats.servers, stats.peripherals]
  );

  const statsArray = useMemo(() => [
    { label: 'Organizations', value: stats.organizations, icon: Building2, color: 'text-blue-500' },
    { label: 'Locations', value: stats.locations, icon: MapPin, color: 'text-green-500' },
    { label: 'Contacts', value: stats.contacts, icon: Users, color: 'text-purple-500' },
    { label: 'Documents', value: stats.documentations, icon: FileText, color: 'text-orange-500' },
    { label: 'Endpoints', value: totalEndpoints, icon: Network, color: 'text-cyan-500' },
    { label: 'Passwords', value: stats.passwords, icon: Lock, color: 'text-red-500' },
    { label: 'Configurations', value: stats.configurations, icon: Wrench, color: 'text-yellow-500' },
  ], [stats, totalEndpoints]);

  return (
    <div className="p-8">
        <PageHeader
          icon={Shield}
          title="Welcome to TechVault"
          subtitle={user?.full_name ? `Hello, ${user.full_name}` : `Hello, ${user?.email}`}
        />

        {/* Welcome Card */}
        <Card className="mb-8 border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Getting Started
            </CardTitle>
            <CardDescription>
              Your enterprise IT documentation platform is ready to use
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              TechVault helps you manage and organize all your IT documentation in one secure place.
              Start by adding your first organization, or explore the features available in the sidebar.
            </p>
            <div className="flex gap-3">
              <div className="px-4 py-2 bg-background rounded-md border border-border">
                <p className="text-xs text-muted-foreground">Account Email</p>
                <p className="font-medium">{user?.email}</p>
              </div>
              <div className="px-4 py-2 bg-background rounded-md border border-border">
                <p className="text-xs text-muted-foreground">Account Status</p>
                <p className="font-medium text-green-500">Active</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {statsArray.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.label} className="hover:border-primary/40 transition-colors">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.label}
                  </CardTitle>
                  <Icon className={`h-5 w-5 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{loading ? '...' : stat.value}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {stat.value === 0 ? 'No items yet' : `${stat.value} item${stat.value !== 1 ? 's' : ''}`}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Info Footer */}
        <div className="mt-8 p-4 bg-muted/50 rounded-lg border border-border">
          <p className="text-sm text-muted-foreground text-center">
            <Shield className="inline h-4 w-4 mr-1" />
            TechVault
          </p>
        </div>
      </div>
  );
};

export default Dashboard;
