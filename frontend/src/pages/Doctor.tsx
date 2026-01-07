import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/contexts/AuthContext';
import { Navigate } from 'react-router-dom';
import {
  Stethoscope,
  Database,
  Server,
  Users,
  Shield,
  HardDrive,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Activity,
  Clock,
  Lock,
  UserCheck,
  Trash2,
  FileText,
  Disc,
} from 'lucide-react';
import { doctorService, SystemHealthResponse } from '@/services/doctor';

type HealthStatus = 'healthy' | 'warning' | 'unhealthy';

const StatusIcon: React.FC<{ status: HealthStatus }> = ({ status }) => {
  switch (status) {
    case 'healthy':
      return <CheckCircle2 className="h-5 w-5 text-green-500" />;
    case 'warning':
      return <AlertTriangle className="h-5 w-5 text-amber-500" />;
    case 'unhealthy':
      return <XCircle className="h-5 w-5 text-red-500" />;
  }
};

const StatusBadge: React.FC<{ status: HealthStatus; label?: string }> = ({ status, label }) => {
  const colors = {
    healthy: 'bg-green-500/10 text-green-500 border-green-500/20',
    warning: 'bg-amber-500/10 text-amber-500 border-amber-500/20',
    unhealthy: 'bg-red-500/10 text-red-500 border-red-500/20',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${colors[status]}`}>
      {label || status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
};

const StatCard: React.FC<{
  icon: React.ElementType;
  label: string;
  value: string | number;
  subtext?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}> = ({ icon: Icon, label, value, subtext, variant = 'default' }) => {
  const variants = {
    default: 'bg-muted/50 text-foreground',
    success: 'bg-green-500/10 text-green-500',
    warning: 'bg-amber-500/10 text-amber-500',
    danger: 'bg-red-500/10 text-red-500',
  };

  return (
    <div className={`p-4 rounded-lg ${variants[variant]}`}>
      <div className="flex items-center gap-2 mb-1">
        <Icon className="h-4 w-4" />
        <span className="text-sm font-medium">{label}</span>
      </div>
      <div className="text-2xl font-bold">{value}</div>
      {subtext && <div className="text-xs opacity-70 mt-1">{subtext}</div>}
    </div>
  );
};

const Doctor: React.FC = () => {
  const { user } = useAuth();
  const [healthData, setHealthData] = useState<SystemHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const isAdmin = user?.is_staff || false;

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await doctorService.getSystemHealth();
      setHealthData(data);
      setLastRefresh(new Date());
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch system health data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchHealthData();
    }
  }, [isAdmin]);

  // Redirect non-admin users
  if (!isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  const formatBytes = (mb: number) => {
    if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`;
    if (mb < 1024) return `${mb.toFixed(2)} MB`;
    return `${(mb / 1024).toFixed(2)} GB`;
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 p-3 rounded-xl border border-primary/20">
              <Stethoscope className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">System Doctor</h1>
              <p className="text-muted-foreground">
                Monitor system health, services, and performance
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {lastRefresh && (
              <span className="text-sm text-muted-foreground">
                Last updated: {lastRefresh.toLocaleTimeString()}
              </span>
            )}
            <Button onClick={fetchHealthData} disabled={loading} variant="outline">
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>
      </div>

      {error && (
        <Card className="mb-6 border-red-500/20 bg-red-500/5">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-500">
              <XCircle className="h-5 w-5" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {loading && !healthData ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <RefreshCw className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
            <p className="text-muted-foreground">Running health checks...</p>
          </div>
        </div>
      ) : healthData ? (
        <>
          {/* Overall Status */}
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-4 rounded-full ${
                    healthData.status === 'healthy' ? 'bg-green-500/10' :
                    healthData.status === 'warning' ? 'bg-amber-500/10' : 'bg-red-500/10'
                  }`}>
                    <Activity className={`h-8 w-8 ${
                      healthData.status === 'healthy' ? 'text-green-500' :
                      healthData.status === 'warning' ? 'text-amber-500' : 'text-red-500'
                    }`} />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold">Overall System Status</h2>
                    <p className="text-muted-foreground">
                      {healthData.status === 'healthy' && 'All systems are operating normally'}
                      {healthData.status === 'warning' && 'Some systems require attention'}
                      {healthData.status === 'unhealthy' && 'Critical issues detected'}
                    </p>
                  </div>
                </div>
                <StatusBadge status={healthData.status} />
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Database Health */}
            {healthData.checks.database && (
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Database className="h-5 w-5" />
                      Database
                    </CardTitle>
                    <StatusIcon status={healthData.checks.database.status} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Engine</span>
                      <span className="font-medium">{healthData.checks.database.engine}</span>
                    </div>
                    {healthData.checks.database.name && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Name</span>
                        <span className="font-medium font-mono text-xs">
                          {typeof healthData.checks.database.name === 'string'
                            ? healthData.checks.database.name.split('/').pop()
                            : 'N/A'}
                        </span>
                      </div>
                    )}
                    {healthData.checks.database.error && (
                      <div className="text-sm text-red-500">{healthData.checks.database.error}</div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Version Info */}
            {healthData.checks.versions && (
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Server className="h-5 w-5" />
                      Versions
                    </CardTitle>
                    <StatusIcon status={healthData.checks.versions.status} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Django</span>
                      <span className="font-medium">{healthData.checks.versions.django}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Python</span>
                      <span className="font-medium">{healthData.checks.versions.python}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Environment</span>
                      <span className={`font-medium px-2 py-0.5 rounded text-xs ${
                        healthData.checks.versions.environment === 'production'
                          ? 'bg-green-500/10 text-green-500'
                          : 'bg-amber-500/10 text-amber-500'
                      }`}>
                        {healthData.checks.versions.environment}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Debug Mode</span>
                      <span className={`font-medium px-2 py-0.5 rounded text-xs ${
                        healthData.checks.versions.debug_mode
                          ? 'bg-amber-500/10 text-amber-500'
                          : 'bg-green-500/10 text-green-500'
                      }`}>
                        {healthData.checks.versions.debug_mode ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Storage */}
            {healthData.checks.storage && (
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <HardDrive className="h-5 w-5" />
                      Storage
                    </CardTitle>
                    <StatusIcon status={healthData.checks.storage.status} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Type</span>
                      <span className="font-medium capitalize">{healthData.checks.storage.type}</span>
                    </div>
                    {healthData.checks.storage.database_size_mb !== undefined && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Database Size</span>
                        <span className="font-medium">{formatBytes(healthData.checks.storage.database_size_mb)}</span>
                      </div>
                    )}
                    {healthData.checks.storage.message && (
                      <div className="text-sm text-muted-foreground">{healthData.checks.storage.message}</div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Disk Space */}
            {healthData.checks.disk_space && (
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Disc className="h-5 w-5" />
                      Disk Space
                    </CardTitle>
                    <StatusIcon status={healthData.checks.disk_space.status} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Path</span>
                      <span className="font-medium font-mono text-xs">{healthData.checks.disk_space.path}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Total</span>
                      <span className="font-medium">{healthData.checks.disk_space.total_gb} GB</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Used</span>
                      <span className="font-medium">{healthData.checks.disk_space.used_gb} GB ({healthData.checks.disk_space.used_percent}%)</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Free</span>
                      <span className={`font-medium ${
                        (healthData.checks.disk_space.free_percent || 0) < 10 ? 'text-red-500' :
                        (healthData.checks.disk_space.free_percent || 0) < 20 ? 'text-amber-500' : 'text-green-500'
                      }`}>
                        {healthData.checks.disk_space.free_gb} GB ({healthData.checks.disk_space.free_percent}%)
                      </span>
                    </div>
                    {/* Disk usage bar */}
                    <div className="pt-2">
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all ${
                            (healthData.checks.disk_space.used_percent || 0) > 90 ? 'bg-red-500' :
                            (healthData.checks.disk_space.used_percent || 0) > 80 ? 'bg-amber-500' : 'bg-primary'
                          }`}
                          style={{ width: `${healthData.checks.disk_space.used_percent || 0}%` }}
                        />
                      </div>
                    </div>
                    {healthData.checks.disk_space.error && (
                      <div className="text-sm text-red-500">{healthData.checks.disk_space.error}</div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Security */}
            {healthData.checks.security && (
              <Card>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Shield className="h-5 w-5" />
                      Security
                    </CardTitle>
                    <StatusIcon status={healthData.checks.security.status} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {[
                      { label: 'HTTPS Enforced', value: healthData.checks.security.https_enforced },
                      { label: 'HSTS Enabled', value: healthData.checks.security.hsts_enabled },
                      { label: 'CSRF Protection', value: healthData.checks.security.csrf_protection },
                      { label: 'Secure Cookies', value: healthData.checks.security.session_cookie_secure },
                      { label: 'Rate Limiting', value: healthData.checks.security.rate_limiting },
                    ].map((item) => (
                      <div key={item.label} className="flex justify-between text-sm">
                        <span className="text-muted-foreground">{item.label}</span>
                        <span className={`font-medium ${item.value ? 'text-green-500' : 'text-amber-500'}`}>
                          {item.value ? 'Yes' : 'No'}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* User Statistics */}
            {healthData.checks.users && (
              <Card className="md:col-span-2">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Users className="h-5 w-5" />
                      User Statistics
                    </CardTitle>
                    <StatusIcon status={healthData.checks.users.status} />
                  </div>
                  {healthData.checks.users.locked_accounts && healthData.checks.users.locked_accounts > 0 && (
                    <CardDescription className="text-amber-500">
                      {healthData.checks.users.locked_accounts} account(s) currently locked
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <StatCard
                      icon={Users}
                      label="Total Users"
                      value={healthData.checks.users.total || 0}
                    />
                    <StatCard
                      icon={UserCheck}
                      label="Active Users"
                      value={healthData.checks.users.active || 0}
                      variant="success"
                    />
                    <StatCard
                      icon={Shield}
                      label="Admins"
                      value={healthData.checks.users.admins || 0}
                    />
                    <StatCard
                      icon={Lock}
                      label="Locked Accounts"
                      value={healthData.checks.users.locked_accounts || 0}
                      variant={healthData.checks.users.locked_accounts ? 'warning' : 'default'}
                    />
                  </div>
                  <div className="mt-4 pt-4 border-t border-border">
                    <h4 className="text-sm font-medium mb-3">2FA Status</h4>
                    <div className="flex items-center gap-4">
                      <div className="flex-1">
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-500 transition-all"
                            style={{ width: `${healthData.checks.users.twofa_percentage || 0}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-sm font-medium">
                        {healthData.checks.users.twofa_percentage || 0}% enabled
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">2FA Enabled</span>
                        <span className="font-medium text-green-500">{healthData.checks.users.twofa_enabled || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">2FA Disabled</span>
                        <span className="font-medium text-amber-500">{healthData.checks.users.twofa_disabled || 0}</span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 pt-4 border-t border-border">
                    <h4 className="text-sm font-medium mb-3">Activity</h4>
                    <div className="grid grid-cols-3 gap-4">
                      <StatCard
                        icon={Clock}
                        label="Logins (24h)"
                        value={healthData.checks.users.recent_logins_24h || 0}
                      />
                      <StatCard
                        icon={Clock}
                        label="Logins (7d)"
                        value={healthData.checks.users.recent_logins_7d || 0}
                      />
                      <StatCard
                        icon={Users}
                        label="Never Logged In"
                        value={healthData.checks.users.never_logged_in || 0}
                        variant={healthData.checks.users.never_logged_in ? 'warning' : 'default'}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Data Statistics */}
            {healthData.checks.data && (
              <Card className="lg:col-span-3">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <FileText className="h-5 w-5" />
                      Data Statistics
                    </CardTitle>
                    <StatusIcon status={healthData.checks.data.status} />
                  </div>
                  <CardDescription>
                    {healthData.checks.data.total_active} active records, {healthData.checks.data.total_deleted} in trash
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                    {healthData.checks.data.active_records && Object.entries(healthData.checks.data.active_records).map(([key, value]) => {
                      const deletedCount = healthData.checks.data?.deleted_records?.[key] || 0;
                      return (
                        <div key={key} className="p-3 rounded-lg bg-muted/50">
                          <div className="text-xs text-muted-foreground mb-1 capitalize">
                            {key.replace(/_/g, ' ')}
                          </div>
                          <div className="text-xl font-bold">{value}</div>
                          {deletedCount > 0 && (
                            <div className="text-xs text-amber-500 flex items-center gap-1 mt-1">
                              <Trash2 className="h-3 w-3" />
                              {deletedCount} deleted
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
};

export default Doctor;
