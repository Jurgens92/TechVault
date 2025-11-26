import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useOrganization } from '@/contexts/OrganizationContext';
import { networkDeviceAPI, endpointUserAPI, serverAPI, peripheralAPI } from '@/services/core';
import type { NetworkDevice, EndpointUser, Server, Peripheral } from '@/types/core';
import { Plus, Network, Monitor, HardDrive, Printer, Loader2, Edit, Trash2 } from 'lucide-react';
import { DeleteConfirmationModal } from '@/components/DeleteConfirmationModal';

export function Endpoints() {
  const { selectedOrg } = useOrganization();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'network' | 'users' | 'servers' | 'peripherals'>('network');
  const [networkDevices, setNetworkDevices] = useState<NetworkDevice[]>([]);
  const [endpointUsers, setEndpointUsers] = useState<EndpointUser[]>([]);
  const [servers, setServers] = useState<Server[]>([]);
  const [peripherals, setPeripherals] = useState<Peripheral[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteModal, setDeleteModal] = useState<{
    isOpen: boolean;
    itemId: string;
    itemName: string;
    itemType: 'network' | 'user' | 'server' | 'peripheral';
  } | null>(null);

  useEffect(() => {
    loadEndpoints();
  }, [selectedOrg]);

  const loadEndpoints = async () => {
    if (!selectedOrg) return;

    try {
      setLoading(true);
      const [networkRes, usersRes, serversRes, peripheralsRes] = await Promise.all([
        networkDeviceAPI.byOrganization(selectedOrg.id),
        endpointUserAPI.byOrganization(selectedOrg.id),
        serverAPI.byOrganization(selectedOrg.id),
        peripheralAPI.byOrganization(selectedOrg.id),
      ]);

      setNetworkDevices(networkRes.data);
      setEndpointUsers(usersRes.data);
      setServers(serversRes.data);
      setPeripherals(peripheralsRes.data);
    } catch (error) {
      console.error('Failed to load endpoints:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (id: string, type: 'network' | 'user' | 'server' | 'peripheral') => {
    const routes = {
      network: `/network-devices/${id}/edit`,
      user: `/endpoint-users/${id}/edit`,
      server: `/servers/${id}/edit`,
      peripheral: `/peripherals/${id}/edit`,
    };
    navigate(routes[type]);
  };

  const handleDeleteClick = (id: string, name: string, type: 'network' | 'user' | 'server' | 'peripheral') => {
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
          Add {activeTab === 'network' ? 'Device' : activeTab === 'users' ? 'Endpoint' : activeTab === 'servers' ? 'Server' : 'Peripheral'}
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
            : 'Peripheral'
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
