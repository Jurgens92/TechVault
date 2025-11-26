import React, { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Shield, Building2, MapPin, Users, FileText, Lock, Wrench, TrendingUp } from 'lucide-react';
import { dashboardAPI } from '@/services/core';

interface DashboardStats {
  organizations: number;
  locations: number;
  contacts: number;
  documentations: number;
  passwords: number;
  configurations: number;
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

  const statsArray = [
    { label: 'Organizations', value: stats.organizations, icon: Building2, color: 'text-blue-500' },
    { label: 'Locations', value: stats.locations, icon: MapPin, color: 'text-green-500' },
    { label: 'Contacts', value: stats.contacts, icon: Users, color: 'text-purple-500' },
    { label: 'Documents', value: stats.documentations, icon: FileText, color: 'text-orange-500' },
    { label: 'Passwords', value: stats.passwords, icon: Lock, color: 'text-red-500' },
    { label: 'Configurations', value: stats.configurations, icon: Wrench, color: 'text-yellow-500' },
  ];

  return (
    <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-primary/10 p-3 rounded-xl border border-primary/20">
              <Shield className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Welcome to TechVault</h1>
              <p className="text-muted-foreground">
                {user?.full_name ? `Hello, ${user.full_name}` : `Hello, ${user?.email}`}
              </p>
            </div>
          </div>
        </div>

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

        {/* Quick Actions */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'Add Organization', path: '/organizations', icon: Building2 },
              { label: 'Add Location', path: '/locations', icon: MapPin },
              { label: 'Add Contact', path: '/contacts', icon: Users },
              { label: 'Create Document', path: '/documentations', icon: FileText },
            ].map((action) => {
              const Icon = action.icon;
              return (
                <Card
                  key={action.label}
                  className="cursor-pointer hover:bg-accent hover:border-primary/40 transition-all"
                >
                  <CardContent className="flex items-center gap-3 p-4">
                    <Icon className="h-5 w-5 text-primary" />
                    <span className="font-medium">{action.label}</span>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Info Footer */}
        <div className="mt-8 p-4 bg-muted/50 rounded-lg border border-border">
          <p className="text-sm text-muted-foreground text-center">
            <Shield className="inline h-4 w-4 mr-1" />
            Your data is secured with enterprise-grade encryption and access controls
          </p>
        </div>
      </div>
  );
};

export default Dashboard;
