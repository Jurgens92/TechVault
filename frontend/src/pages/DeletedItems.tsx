import React, { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { ListHeader } from '../components/ListHeader';
import { RestoreIcon, Trash2, RefreshCw } from 'lucide-react';
import {
  organizationAPI, locationAPI, contactAPI, documentationAPI,
  passwordAPI, configurationAPI, networkDeviceAPI, endpointUserAPI,
  serverAPI, peripheralAPI
} from '../services/core';

type EntityType =
  | 'organizations'
  | 'locations'
  | 'contacts'
  | 'documentations'
  | 'passwords'
  | 'configurations'
  | 'network-devices'
  | 'endpoints'
  | 'servers'
  | 'peripherals';

const DeletedItems: React.FC = () => {
  const [activeTab, setActiveTab] = useState<EntityType>('organizations');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // State for each entity type
  const [deletedItems, setDeletedItems] = useState<Record<EntityType, any[]>>({
    organizations: [],
    locations: [],
    contacts: [],
    documentations: [],
    passwords: [],
    configurations: [],
    'network-devices': [],
    endpoints: [],
    servers: [],
    peripherals: [],
  });

  const entityConfig = {
    organizations: { api: organizationAPI, label: 'Organizations', nameField: 'name' },
    locations: { api: locationAPI, label: 'Locations', nameField: 'name' },
    contacts: { api: contactAPI, label: 'Contacts', nameField: 'full_name' },
    documentations: { api: documentationAPI, label: 'Documentation', nameField: 'title' },
    passwords: { api: passwordAPI, label: 'Passwords', nameField: 'name' },
    configurations: { api: configurationAPI, label: 'Configurations', nameField: 'name' },
    'network-devices': { api: networkDeviceAPI, label: 'Network Devices', nameField: 'name' },
    endpoints: { api: endpointUserAPI, label: 'Endpoints', nameField: 'name' },
    servers: { api: serverAPI, label: 'Servers', nameField: 'name' },
    peripherals: { api: peripheralAPI, label: 'Peripherals', nameField: 'name' },
  };

  useEffect(() => {
    loadAllDeletedItems();
  }, []);

  const loadAllDeletedItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const results = await Promise.all([
        organizationAPI.getDeleted(),
        locationAPI.getDeleted(),
        contactAPI.getDeleted(),
        documentationAPI.getDeleted(),
        passwordAPI.getDeleted(),
        configurationAPI.getDeleted(),
        networkDeviceAPI.getDeleted(),
        endpointUserAPI.getDeleted(),
        serverAPI.getDeleted(),
        peripheralAPI.getDeleted(),
      ]);

      setDeletedItems({
        organizations: results[0].data.results || [],
        locations: results[1].data.results || [],
        contacts: results[2].data.results || [],
        documentations: results[3].data.results || [],
        passwords: results[4].data.results || [],
        configurations: results[5].data.results || [],
        'network-devices': results[6].data.results || [],
        endpoints: results[7].data.results || [],
        servers: results[8].data.results || [],
        peripherals: results[9].data.results || [],
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load deleted items');
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (id: string, entityType: EntityType) => {
    try {
      const config = entityConfig[entityType];
      await config.api.restore(id);
      setSuccess(`${config.label} item restored successfully!`);
      setTimeout(() => setSuccess(null), 3000);
      loadAllDeletedItems();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to restore item`);
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleHardDelete = async (id: string, entityType: EntityType) => {
    const config = entityConfig[entityType];
    if (!window.confirm(`Are you sure you want to PERMANENTLY delete this ${config.label} item? This action cannot be undone!`)) {
      return;
    }
    try {
      await config.api.hardDelete(id);
      setSuccess(`${config.label} item permanently deleted!`);
      setTimeout(() => setSuccess(null), 3000);
      loadAllDeletedItems();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to permanently delete item`);
      setTimeout(() => setError(null), 5000);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const currentItems = deletedItems[activeTab];
  const config = entityConfig[activeTab];

  return (
    <div className="space-y-6">
      <ListHeader
        title="Deleted Items"
        subtitle="Restore or permanently delete items"
        hideAddButton
        hideSearch
      />

      {error && (
        <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200 flex justify-between items-center">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">×</button>
        </div>
      )}

      {success && (
        <div className="p-4 bg-green-900/20 border border-green-700 rounded-lg text-green-200 flex justify-between items-center">
          <span>{success}</span>
          <button onClick={() => setSuccess(null)} className="text-green-400 hover:text-green-300">×</button>
        </div>
      )}

      {/* Tab Navigation */}
      <Card>
        <div className="border-b border-border overflow-x-auto">
          <div className="flex min-w-max">
            {Object.entries(entityConfig).map(([key, value]) => {
              const count = deletedItems[key as EntityType].length;
              return (
                <button
                  key={key}
                  onClick={() => setActiveTab(key as EntityType)}
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                    activeTab === key
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
                  }`}
                >
                  {value.label} ({count})
                </button>
              );
            })}
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <p className="mt-4 text-gray-400">Loading deleted items...</p>
            </div>
          ) : currentItems.length === 0 ? (
            <div className="text-center py-12">
              <Trash2 className="mx-auto h-12 w-12 text-muted-foreground/50" />
              <h3 className="mt-4 text-lg font-semibold">No deleted items</h3>
              <p className="text-muted-foreground">
                No deleted {config.label.toLowerCase()} found
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 font-semibold text-sm">Name</th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">Deleted At</th>
                    <th className="text-left py-3 px-4 font-semibold text-sm">Deleted By</th>
                    <th className="text-right py-3 px-4 font-semibold text-sm">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {currentItems.map((item: any) => (
                    <tr key={item.id} className="border-b border-border/50 hover:bg-accent/5">
                      <td className="py-3 px-4">
                        <div className="font-medium">
                          {item[config.nameField] || item.title || 'N/A'}
                        </div>
                        {item.organization_name && (
                          <div className="text-sm text-muted-foreground">
                            {item.organization_name}
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">
                        {formatDate(item.deleted_at)}
                      </td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">
                        {item.deleted_by
                          ? `${item.deleted_by.first_name} ${item.deleted_by.last_name}`
                          : 'N/A'}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRestore(item.id, activeTab)}
                            className="flex items-center gap-1"
                          >
                            <RefreshCw className="h-4 w-4" />
                            Restore
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleHardDelete(item.id, activeTab)}
                            className="flex items-center gap-1"
                          >
                            <Trash2 className="h-4 w-4" />
                            Delete Forever
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default DeletedItems;
