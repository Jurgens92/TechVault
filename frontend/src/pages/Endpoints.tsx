import { useEffect, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useOrganization } from '@/contexts/OrganizationContext';
import { networkDeviceAPI, endpointUserAPI, serverAPI, peripheralAPI, backupAPI, softwareAPI } from '@/services/core';
import type { NetworkDevice, EndpointUser, Server, Peripheral, Backup, Software } from '@/types/core';
import { Plus, Network, Monitor, HardDrive, Printer, Database, Package, Loader2, Edit, Trash2 } from 'lucide-react';
import { DeleteConfirmationModal } from '@/components/DeleteConfirmationModal';

export function Endpoints() {
  const { selectedOrg } = useOrganization();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Read the tab from the URL query parameter, default to 'network' if not present
  const tabFromUrl = searchParams.get('tab') as 'network' | 'users' | 'servers' | 'peripherals' | 'backups' | 'software' | null;
  const initialTab = tabFromUrl && ['network', 'users', 'servers', 'peripherals', 'backups', 'software'].includes(tabFromUrl)
    ? tabFromUrl
    : 'network';

  const [activeTab, setActiveTab] = useState<'network' | 'users' | 'servers' | 'peripherals' | 'backups' | 'software'>(initialTab);
  const [networkDevices, setNetworkDevices] = useState<NetworkDevice[]>([]);
  const [endpointUsers, setEndpointUsers] = useState<EndpointUser[]>([]);
  const [servers, setServers] = useState<Server[]>([]);
  const [peripherals, setPeripherals] = useState<Peripheral[]>([]);
  const [backups, setBackups] = useState<Backup[]>([]);
  const [software, setSoftware] = useState<Software[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    itemId: string;
    itemName: string;
    itemType: 'network' | 'user' | 'server' | 'peripheral' | 'backup' | 'software';
  } | null>(null);

  useEffect(() => {
    loadEndpoints();
  }, [selectedOrg]);

  const loadEndpoints = async () => {
    if (!selectedOrg) return;

    try {
      setLoading(true);
      const [networkRes, usersRes, serversRes, peripheralsRes, backupsRes, softwareRes] = await Promise.all([
        networkDeviceAPI.byOrganization(selectedOrg.id),
        endpointUserAPI.byOrganization(selectedOrg.id),
        serverAPI.byOrganization(selectedOrg.id),
        peripheralAPI.byOrganization(selectedOrg.id),
        backupAPI.byOrganization(selectedOrg.id),
        softwareAPI.byOrganization(selectedOrg.id),
      ]);

      setNetworkDevices(networkRes.data);
      setEndpointUsers(usersRes.data);
      setServers(serversRes.data);
      setPeripherals(peripheralsRes.data);
      setBackups(backupsRes.data);
      setSoftware(softwareRes.data);
    } catch (error) {
      console.error('Failed to load endpoints:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (id: string, type: 'network' | 'user' | 'server' | 'peripheral' | 'backup' | 'software') => {
    const routes = {
      network: `/network-devices/${id}/edit`,
      user: `/endpoint-users/${id}/edit`,
      server: `/servers/${id}/edit`,
      peripheral: `/peripherals/${id}/edit`,
      backup: `/backups/${id}/edit`,
      software: `/software/${id}/edit`,
    };
    navigate(routes[type]);
  };

  const handleDeleteClick = (id: string, name: string, type: 'network' | 'user' | 'server' | 'peripheral' | 'backup' | 'software') => {
    setDeleteModal({
      isOpen: true,
      itemId: id,
      itemName: name,
      itemType: type,
    });
  };

  const handleDeleteConfirm = async () => {
    if (!deleteModal) return;

    try {
      const apiMap = {
        network: networkDeviceAPI,
        user: endpointUserAPI,
        server: serverAPI,
        peripheral: peripheralAPI,
        backup: backupAPI,
        software: softwareAPI,
      };

      await apiMap[deleteModal.itemType].delete(deleteModal.itemId);

      // Update local state to remove deleted item
      switch (deleteModal.itemType) {
        case 'network':
          setNetworkDevices((prev) => prev.filter((d) => d.id !== deleteModal.itemId));
          break;
        case 'user':
          setEndpointUsers((prev) => prev.filter((u) => u.id !== deleteModal.itemId));
          break;
        case 'server':
          setServers((prev) => prev.filter((s) => s.id !== deleteModal.itemId));
          break;
        case 'peripheral':
          setPeripherals((prev) => prev.filter((p) => p.id !== deleteModal.itemId));
          break;
        case 'backup':
          setBackups((prev) => prev.filter((b) => b.id !== deleteModal.itemId));
          break;
        case 'software':
          setSoftware((prev) => prev.filter((sw) => sw.id !== deleteModal.itemId));
          break;
      }
    } catch (error) {
      console.error('Failed to delete item:', error);
      throw error; // Re-throw so the modal can handle the error state
    }
  };

  const tabs = [
    { id: 'network' as const, label: 'Network', icon: Network, count: networkDevices.length },
    { id: 'users' as const, label: 'Users', icon: Monitor, count: endpointUsers.length },
    { id: 'servers' as const, label: 'Servers', icon: HardDrive, count: servers.length },
    { id: 'peripherals' as const, label: 'Peripherals', icon: Printer, count: peripherals.length },
    { id: 'backups' as const, label: 'Backups', icon: Database, count: backups.length },
    { id: 'software' as const, label: 'Software', icon: Package, count: software.length },
  ];

  if (!selectedOrg) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <p className="text-muted-foreground">Please select an organization to view endpoints</p>
        </div>
      </div>
    );
  }

  const getAddRoute = () => {
    switch (activeTab) {
      case 'network': return '/network-devices/new';
      case 'users': return '/endpoint-users/new';
      case 'servers': return '/servers/new';
      case 'peripherals': return '/peripherals/new';
      case 'backups': return '/backups/new';
      case 'software': return '/software/new';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Endpoints</h1>
          <p className="text-muted-foreground mt-1">
            Manage your network infrastructure and devices
          </p>
        </div>
        <button
          onClick={() => navigate(getAddRoute())}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          disabled={!selectedOrg}
        >
          <Plus className="h-4 w-4" />
          Add {activeTab === 'network' ? 'Device' : activeTab === 'users' ? 'Endpoint' : activeTab === 'servers' ? 'Server' : activeTab === 'peripherals' ? 'Peripheral' : activeTab === 'backups' ? 'Backup' : 'Software'}
        </button>
      </div>

      <div className="border-b border-border">
        <div className="flex space-x-4">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{tab.label}</span>
                <span className="ml-1 px-2 py-0.5 text-xs rounded-full bg-accent">
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : (
        <>
          {activeTab === 'network' && (
            <NetworkDevicesList
              devices={networkDevices}
              onEdit={(id) => handleEdit(id, 'network')}
              onDelete={(id, name) => handleDeleteClick(id, name, 'network')}
            />
          )}
          {activeTab === 'users' && (
            <EndpointUsersList
              users={endpointUsers}
              onEdit={(id) => handleEdit(id, 'user')}
              onDelete={(id, name) => handleDeleteClick(id, name, 'user')}
            />
          )}
          {activeTab === 'servers' && (
            <ServersList
              servers={servers}
              onEdit={(id) => handleEdit(id, 'server')}
              onDelete={(id, name) => handleDeleteClick(id, name, 'server')}
            />
          )}
          {activeTab === 'peripherals' && (
            <PeripheralsList
              peripherals={peripherals}
              onEdit={(id) => handleEdit(id, 'peripheral')}
              onDelete={(id, name) => handleDeleteClick(id, name, 'peripheral')}
            />
          )}
          {activeTab === 'backups' && (
            <BackupsList
              backups={backups}
              onEdit={(id) => handleEdit(id, 'backup')}
              onDelete={(id, name) => handleDeleteClick(id, name, 'backup')}
            />
          )}
          {activeTab === 'software' && (
            <SoftwareList
              software={software}
              onEdit={(id) => handleEdit(id, 'software')}
              onDelete={(id, name) => handleDeleteClick(id, name, 'software')}
            />
          )}
        </>
      )}

      <DeleteConfirmationModal
        isOpen={deleteModal?.isOpen ?? false}
        onClose={() => setDeleteModal(null)}
        onConfirm={handleDeleteConfirm}
        itemName={deleteModal?.itemName ?? ''}
        itemType={
          deleteModal?.itemType === 'network'
            ? 'Network Device'
            : deleteModal?.itemType === 'user'
            ? 'Endpoint User'
            : deleteModal?.itemType === 'server'
            ? 'Server'
            : deleteModal?.itemType === 'peripheral'
            ? 'Peripheral'
            : deleteModal?.itemType === 'backup'
            ? 'Backup'
            : 'Software'
        }
      />
    </div>
  );
}

function NetworkDevicesList({
  devices,
  onEdit,
  onDelete,
}: {
  devices: NetworkDevice[];
  onEdit: (id: string) => void;
  onDelete: (id: string, name: string) => void;
}) {
  return (
    <div className="space-y-4">
      {devices.length === 0 ? (
        <div className="text-center py-12 border border-dashed rounded-lg">
          <Network className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-4">No network devices found</p>
          <p className="text-sm text-muted-foreground">
            Add your first network device to get started
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {devices.map((device) => (
            <div
              key={device.id}
              className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold">{device.name}</h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 rounded bg-accent">
                    {device.device_type}
                  </span>
                  <button
                    onClick={() => onEdit(device.id)}
                    className="text-muted-foreground hover:text-primary transition-colors"
                    title="Edit"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onDelete(device.id, device.name)}
                    className="text-muted-foreground hover:text-destructive transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              {device.manufacturer && (
                <p className="text-sm text-muted-foreground">
                  {device.manufacturer} {device.model}
                </p>
              )}
              {device.ip_address && (
                <p className="text-sm text-muted-foreground mt-1">IP: {device.ip_address}</p>
              )}
              {device.internet_provider && (
                <p className="text-sm text-muted-foreground mt-1">
                  Provider: {device.internet_provider} ({device.internet_speed})
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function EndpointUsersList({
  users,
  onEdit,
  onDelete,
}: {
  users: EndpointUser[];
  onEdit: (id: string) => void;
  onDelete: (id: string, name: string) => void;
}) {
  return (
    <div className="space-y-4">
      {users.length === 0 ? (
        <div className="text-center py-12 border border-dashed rounded-lg">
          <Monitor className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-4">No user endpoints found</p>
          <p className="text-sm text-muted-foreground">
            Add your first desktop or laptop to get started
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {users.map((user) => (
            <div
              key={user.id}
              className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold">{user.name}</h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 rounded bg-accent">
                    {user.device_type}
                  </span>
                  <button
                    onClick={() => onEdit(user.id)}
                    className="text-muted-foreground hover:text-primary transition-colors"
                    title="Edit"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onDelete(user.id, user.name)}
                    className="text-muted-foreground hover:text-destructive transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              {user.assigned_to_name && (
                <p className="text-sm text-muted-foreground">User: {user.assigned_to_name}</p>
              )}
              {user.cpu && (
                <p className="text-sm text-muted-foreground mt-1">
                  {user.cpu} • {user.ram}
                </p>
              )}
              {user.operating_system && (
                <p className="text-sm text-muted-foreground mt-1">{user.operating_system}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ServersList({
  servers,
  onEdit,
  onDelete,
}: {
  servers: Server[];
  onEdit: (id: string) => void;
  onDelete: (id: string, name: string) => void;
}) {
  return (
    <div className="space-y-4">
      {servers.length === 0 ? (
        <div className="text-center py-12 border border-dashed rounded-lg">
          <HardDrive className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-4">No servers found</p>
          <p className="text-sm text-muted-foreground">
            Add your first server to get started
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {servers.map((server) => (
            <div
              key={server.id}
              className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold">{server.name}</h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 rounded bg-accent">
                    {server.server_type}
                  </span>
                  <button
                    onClick={() => onEdit(server.id)}
                    className="text-muted-foreground hover:text-primary transition-colors"
                    title="Edit"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onDelete(server.id, server.name)}
                    className="text-muted-foreground hover:text-destructive transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              {server.role && (
                <p className="text-sm text-muted-foreground">Role: {server.role}</p>
              )}
              {server.cpu && (
                <p className="text-sm text-muted-foreground mt-1">
                  {server.cpu} • {server.ram}
                </p>
              )}
              {server.operating_system && (
                <p className="text-sm text-muted-foreground mt-1">{server.operating_system}</p>
              )}
              {server.ip_address && (
                <p className="text-sm text-muted-foreground mt-1">IP: {server.ip_address}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function PeripheralsList({
  peripherals,
  onEdit,
  onDelete,
}: {
  peripherals: Peripheral[];
  onEdit: (id: string) => void;
  onDelete: (id: string, name: string) => void;
}) {
  return (
    <div className="space-y-4">
      {peripherals.length === 0 ? (
        <div className="text-center py-12 border border-dashed rounded-lg">
          <Printer className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-4">No peripherals found</p>
          <p className="text-sm text-muted-foreground">
            Add your first printer or peripheral to get started
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {peripherals.map((peripheral) => (
            <div
              key={peripheral.id}
              className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold">{peripheral.name}</h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 rounded bg-accent">
                    {peripheral.device_type}
                  </span>
                  <button
                    onClick={() => onEdit(peripheral.id)}
                    className="text-muted-foreground hover:text-primary transition-colors"
                    title="Edit"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onDelete(peripheral.id, peripheral.name)}
                    className="text-muted-foreground hover:text-destructive transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              {peripheral.manufacturer && (
                <p className="text-sm text-muted-foreground">
                  {peripheral.manufacturer} {peripheral.model}
                </p>
              )}
              {peripheral.ip_address && (
                <p className="text-sm text-muted-foreground mt-1">IP: {peripheral.ip_address}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function BackupsList({
  backups,
  onEdit,
  onDelete,
}: {
  backups: Backup[];
  onEdit: (id: string) => void;
  onDelete: (id: string, name: string) => void;
}) {
  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-4">
      {backups.length === 0 ? (
        <div className="text-center py-12 border border-dashed rounded-lg">
          <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-4">No backups found</p>
          <p className="text-sm text-muted-foreground">
            Add your first backup solution to get started
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
          {backups.map((backup) => (
            <div
              key={backup.id}
              className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">{backup.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs px-2 py-1 rounded bg-accent capitalize">
                      {backup.backup_type.replace(/_/g, ' ')}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded font-medium ${
                      backup.backup_status === 'active'
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : backup.backup_status === 'failed'
                        ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        : backup.backup_status === 'warning'
                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
                    }`}>
                      {backup.backup_status}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-2">
                  <button
                    onClick={() => onEdit(backup.id)}
                    className="text-muted-foreground hover:text-primary transition-colors"
                    title="Edit"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onDelete(backup.id, backup.name)}
                    className="text-muted-foreground hover:text-destructive transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                {backup.vendor && (
                  <div className="flex items-start">
                    <span className="text-muted-foreground min-w-[100px]">Vendor:</span>
                    <span className="font-medium">{backup.vendor}</span>
                  </div>
                )}
                {backup.frequency && (
                  <div className="flex items-start">
                    <span className="text-muted-foreground min-w-[100px]">Frequency:</span>
                    <span className="font-medium">{backup.frequency}</span>
                  </div>
                )}
                {backup.retention_period && (
                  <div className="flex items-start">
                    <span className="text-muted-foreground min-w-[100px]">Retention:</span>
                    <span className="font-medium">{backup.retention_period}</span>
                  </div>
                )}
                {backup.storage_location && (
                  <div className="flex items-start">
                    <span className="text-muted-foreground min-w-[100px]">Storage:</span>
                    <span className="font-medium">{backup.storage_location}</span>
                  </div>
                )}
                {backup.storage_capacity && (
                  <div className="flex items-start">
                    <span className="text-muted-foreground min-w-[100px]">Capacity:</span>
                    <span className="font-medium">{backup.storage_capacity}</span>
                  </div>
                )}
                {backup.target_systems && (
                  <div className="flex items-start">
                    <span className="text-muted-foreground min-w-[100px]">Targets:</span>
                    <span className="font-medium line-clamp-2">{backup.target_systems}</span>
                  </div>
                )}
                {backup.last_backup_date && (
                  <div className="flex items-start">
                    <span className="text-muted-foreground min-w-[100px]">Last Backup:</span>
                    <span className="font-medium text-xs">{formatDate(backup.last_backup_date)}</span>
                  </div>
                )}
                {backup.cost && (
                  <div className="flex items-start">
                    <span className="text-muted-foreground min-w-[100px]">Cost:</span>
                    <span className="font-medium">
                      ${backup.cost.toFixed(2)}/{backup.cost_period || 'month'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SoftwareList({
  software,
  onEdit,
  onDelete,
}: {
  software: Software[];
  onEdit: (id: string) => void;
  onDelete: (id: string, name: string) => void;
}) {
  return (
    <div className="space-y-4">
      {software.length === 0 ? (
        <div className="text-center py-12 border border-dashed rounded-lg">
          <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground mb-4">No software found</p>
          <p className="text-sm text-muted-foreground">
            Add your first software to get started
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {software.map((sw) => (
            <div
              key={sw.id}
              className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold">{sw.name}</h3>
                <div className="flex items-center gap-2">
                  <span className="text-xs px-2 py-1 rounded bg-accent">
                    {sw.software_type}
                  </span>
                  <button
                    onClick={() => onEdit(sw.id)}
                    className="text-muted-foreground hover:text-primary transition-colors"
                    title="Edit"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onDelete(sw.id, sw.name)}
                    className="text-muted-foreground hover:text-destructive transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              {sw.assigned_to_name && (
                <p className="text-sm text-muted-foreground">
                  User: {sw.assigned_to_name}
                </p>
              )}
              {sw.vendor && (
                <p className="text-sm text-muted-foreground">
                  {sw.vendor}
                </p>
              )}
              {sw.expiry_date && (
                <p className="text-sm text-muted-foreground mt-1">
                  Expires: {new Date(sw.expiry_date).toLocaleDateString()}
                </p>
              )}
              {sw.version && (
                <p className="text-sm text-muted-foreground">
                  Version: {sw.version}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
