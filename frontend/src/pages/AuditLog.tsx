import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { PageHeader } from '@/components/PageHeader';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import {
  ClipboardList,
  Search,
  ChevronLeft,
  ChevronRight,
  Filter,
  X,
  Plus,
  Pencil,
  Trash2,
  RotateCcw,
  LogIn,
  LogOut,
  Download,
  Upload,
  User,
} from 'lucide-react';
import { auditAPI, AuditLogEntry } from '@/services/audit';

const ACTION_LABELS: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  create: { label: 'Created', color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400', icon: <Plus className="h-3.5 w-3.5" /> },
  update: { label: 'Updated', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400', icon: <Pencil className="h-3.5 w-3.5" /> },
  delete: { label: 'Deleted', color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400', icon: <Trash2 className="h-3.5 w-3.5" /> },
  restore: { label: 'Restored', color: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400', icon: <RotateCcw className="h-3.5 w-3.5" /> },
  login: { label: 'Login', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400', icon: <LogIn className="h-3.5 w-3.5" /> },
  logout: { label: 'Logout', color: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400', icon: <LogOut className="h-3.5 w-3.5" /> },
  export: { label: 'Exported', color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400', icon: <Download className="h-3.5 w-3.5" /> },
  import: { label: 'Imported', color: 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-400', icon: <Upload className="h-3.5 w-3.5" /> },
};

const ENTITY_TYPES = [
  'Organization', 'Location', 'Contact', 'Documentation',
  'PasswordEntry', 'Configuration', 'NetworkDevice', 'EndpointUser',
  'Server', 'Peripheral', 'Software', 'Backup', 'VoIP',
];

const ACTION_TYPES = ['create', 'update', 'delete', 'restore'];

const formatEntityType = (type: string): string => {
  return type
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, s => s.toUpperCase())
    .trim();
};

const formatTimestamp = (ts: string): string => {
  const date = new Date(ts);
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

const AuditLog: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [entityTypeFilter, setEntityTypeFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const pageSize = 50;

  const loadLogs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params: Record<string, any> = { page: currentPage };
      if (searchQuery) params.search = searchQuery;
      if (actionFilter) params.action = actionFilter;
      if (entityTypeFilter) params.entity_type = entityTypeFilter;
      const response = await auditAPI.getAll(params);
      setLogs(response.data.results || []);
      setTotalCount(response.data.count || 0);
    } catch (err: any) {
      console.error('Failed to load audit logs:', err);
      setError(err.response?.data?.detail || 'Failed to load audit logs.');
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchQuery, actionFilter, entityTypeFilter]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  const totalPages = Math.ceil(totalCount / pageSize);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    loadLogs();
  };

  const clearFilters = () => {
    setSearchQuery('');
    setActionFilter('');
    setEntityTypeFilter('');
    setCurrentPage(1);
  };

  const hasActiveFilters = searchQuery || actionFilter || entityTypeFilter;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audit Log"
        subtitle="Track all user actions across the platform"
        icon={ClipboardList}
      />

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Activity History</CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant={showFilters ? 'default' : 'outline'}
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-4 w-4 mr-1" />
                Filters
                {hasActiveFilters && (
                  <span className="ml-1 bg-primary-foreground text-primary rounded-full h-5 w-5 flex items-center justify-center text-xs">
                    !
                  </span>
                )}
              </Button>
              {hasActiveFilters && (
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  <X className="h-4 w-4 mr-1" />
                  Clear
                </Button>
              )}
            </div>
          </div>

          {showFilters && (
            <div className="mt-4 flex flex-wrap items-end gap-3">
              <form onSubmit={handleSearch} className="flex-1 min-w-[200px]">
                <label className="text-xs font-medium text-muted-foreground mb-1 block">Search</label>
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    className="pl-9"
                    placeholder="Search by name, type, user..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </form>
              <div className="min-w-[150px]">
                <label className="text-xs font-medium text-muted-foreground mb-1 block">Action</label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={actionFilter}
                  onChange={(e) => { setActionFilter(e.target.value); setCurrentPage(1); }}
                >
                  <option value="">All Actions</option>
                  {ACTION_TYPES.map(a => (
                    <option key={a} value={a}>{a.charAt(0).toUpperCase() + a.slice(1)}</option>
                  ))}
                </select>
              </div>
              <div className="min-w-[170px]">
                <label className="text-xs font-medium text-muted-foreground mb-1 block">Entity Type</label>
                <select
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={entityTypeFilter}
                  onChange={(e) => { setEntityTypeFilter(e.target.value); setCurrentPage(1); }}
                >
                  <option value="">All Types</option>
                  {ENTITY_TYPES.map(t => (
                    <option key={t} value={t}>{formatEntityType(t)}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </CardHeader>

        <CardContent>
          {error && (
            <div className="mb-4 p-3 bg-destructive/10 text-destructive rounded-md text-sm">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-muted-foreground">Loading audit logs...</div>
            </div>
          ) : logs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <ClipboardList className="h-12 w-12 mb-3 opacity-50" />
              <p className="text-lg font-medium">No audit logs found</p>
              <p className="text-sm">
                {hasActiveFilters
                  ? 'Try adjusting your filters.'
                  : 'Actions will appear here as users interact with the system.'}
              </p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left">
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Timestamp</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">User</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Action</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Type</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Name</th>
                      <th className="pb-3 pr-4 font-medium text-muted-foreground">Organization</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log) => {
                      const actionInfo = ACTION_LABELS[log.action] || {
                        label: log.action,
                        color: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
                        icon: null,
                      };
                      return (
                        <tr key={log.id} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                          <td className="py-3 pr-4 text-muted-foreground whitespace-nowrap">
                            {formatTimestamp(log.timestamp)}
                          </td>
                          <td className="py-3 pr-4">
                            <div className="flex items-center gap-2">
                              <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center">
                                <User className="h-3.5 w-3.5 text-primary" />
                              </div>
                              <div>
                                <div className="font-medium text-sm">{log.user_name || 'System'}</div>
                                <div className="text-xs text-muted-foreground">{log.user_email}</div>
                              </div>
                            </div>
                          </td>
                          <td className="py-3 pr-4">
                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${actionInfo.color}`}>
                              {actionInfo.icon}
                              {actionInfo.label}
                            </span>
                          </td>
                          <td className="py-3 pr-4 text-muted-foreground">
                            {formatEntityType(log.entity_type)}
                          </td>
                          <td className="py-3 pr-4 font-medium max-w-[200px] truncate" title={log.entity_name}>
                            {log.entity_name || '-'}
                          </td>
                          <td className="py-3 pr-4 text-muted-foreground max-w-[150px] truncate" title={log.organization_name}>
                            {log.organization_name || '-'}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
                  <div className="text-sm text-muted-foreground">
                    Showing {((currentPage - 1) * pageSize) + 1}-{Math.min(currentPage * pageSize, totalCount)} of {totalCount} entries
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={currentPage <= 1}
                      onClick={() => setCurrentPage(p => p - 1)}
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <span className="text-sm text-muted-foreground">
                      Page {currentPage} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={currentPage >= totalPages}
                      onClick={() => setCurrentPage(p => p + 1)}
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AuditLog;
