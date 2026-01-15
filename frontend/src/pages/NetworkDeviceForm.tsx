import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOrganization } from '@/contexts/OrganizationContext';
import { networkDeviceAPI, locationAPI } from '@/services/core';
import type { NetworkDevice, Location, InternetConnection } from '@/types/core';
import { ArrowLeft, Loader2, Plus, Trash2 } from 'lucide-react';

const emptyConnection: Omit<InternetConnection, 'id' | 'created_at' | 'updated_at' | 'speed_display'> = {
  provider_name: '',
  connection_type: 'fiber',
  download_speed: 100,
  upload_speed: 100,
  is_primary: false,
  account_number: '',
  notes: '',
  is_active: true,
};

export function NetworkDeviceForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState<Location[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    device_type: 'other' as NetworkDevice['device_type'],
    internet_provider: '',
    internet_speed: '',
    manufacturer: '',
    model: '',
    ip_address: '',
    mac_address: '',
    serial_number: '',
    firmware_version: '',
    location: '',
    notes: '',
    is_active: true,
  });
  const [internetConnections, setInternetConnections] = useState<Partial<InternetConnection>[]>([]);

  useEffect(() => {
    if (selectedOrg) {
      loadLocations();
    }
    if (id) {
      loadDevice();
    }
  }, [id, selectedOrg]);

  const loadLocations = async () => {
    if (!selectedOrg) return;
    try {
      const response = await locationAPI.byOrganization(selectedOrg.id);
      // Sort by creation date (oldest first)
      const sortedLocations = response.data.sort((a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      setLocations(sortedLocations);

      // If creating a new device (not editing), pre-select the first location
      if (!id && sortedLocations.length > 0) {
        setFormData((prev) => ({ ...prev, location: sortedLocations[0].id }));
      }
    } catch (error) {
      console.error('Failed to load locations:', error);
    }
  };

  const loadDevice = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await networkDeviceAPI.getById(id);
      const device = response.data;
      setFormData({
        name: device.name,
        device_type: device.device_type,
        internet_provider: device.internet_provider,
        internet_speed: device.internet_speed,
        manufacturer: device.manufacturer,
        model: device.model,
        ip_address: device.ip_address,
        mac_address: device.mac_address,
        serial_number: device.serial_number,
        firmware_version: device.firmware_version,
        location: device.location || '',
        notes: device.notes,
        is_active: device.is_active,
      });
      // Load internet connections if available
      if (device.internet_connections && device.internet_connections.length > 0) {
        setInternetConnections(device.internet_connections);
      }
    } catch (error) {
      console.error('Failed to load device:', error);
    } finally {
      setLoading(false);
    }
  };

  const addConnection = () => {
    const isFirst = internetConnections.length === 0;
    setInternetConnections([...internetConnections, { ...emptyConnection, is_primary: isFirst }]);
  };

  const removeConnection = (index: number) => {
    const updated = internetConnections.filter((_, i) => i !== index);
    // If we removed the primary, make the first one primary
    if (updated.length > 0 && !updated.some(c => c.is_primary)) {
      updated[0].is_primary = true;
    }
    setInternetConnections(updated);
  };

  const updateConnection = (index: number, field: keyof InternetConnection, value: any) => {
    const updated = [...internetConnections];
    updated[index] = { ...updated[index], [field]: value };
    // If setting this as primary, unset others
    if (field === 'is_primary' && value === true) {
      updated.forEach((conn, i) => {
        if (i !== index) conn.is_primary = false;
      });
    }
    setInternetConnections(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOrg) return;

    try {
      setLoading(true);
      // Filter out incomplete connections (must have provider_name)
      const validConnections = internetConnections
        .filter(conn => conn.provider_name && conn.provider_name.trim())
        .map(conn => ({
          provider_name: conn.provider_name,
          connection_type: conn.connection_type || 'fiber',
          download_speed: conn.download_speed || 100,
          upload_speed: conn.upload_speed || 100,
          is_primary: conn.is_primary || false,
          account_number: conn.account_number || '',
          notes: conn.notes || '',
          is_active: conn.is_active !== false,
        }));

      const data = {
        ...formData,
        organization: selectedOrg.id,
        location: formData.location || null,
        internet_connections: validConnections,
      };

      if (id) {
        await networkDeviceAPI.update(id, data);
      } else {
        await networkDeviceAPI.create(data);
      }

      navigate('/endpoints?tab=network');
    } catch (error) {
      console.error('Failed to save device:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedOrg) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <p className="text-muted-foreground">Please select an organization first</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-3xl">
      <button
        onClick={() => navigate('/endpoints')}
        className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Endpoints
      </button>

      <h1 className="text-3xl font-bold mb-6">
        {id ? 'Edit Network Device' : 'Add Network Device'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          <div>
            <label className="block text-sm font-medium mb-2">
              Name <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Device Type <span className="text-destructive">*</span>
            </label>
            <select
              value={formData.device_type}
              onChange={(e) => setFormData({ ...formData, device_type: e.target.value as NetworkDevice['device_type'] })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
            >
              <option value="firewall">Firewall</option>
              <option value="router">Router</option>
              <option value="firewall_router">Firewall/Router</option>
              <option value="switch">Switch</option>
              <option value="wifi">WiFi Access Point</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Manufacturer</label>
              <input
                type="text"
                value={formData.manufacturer}
                onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Model</label>
              <input
                type="text"
                value={formData.model}
                onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
              />
            </div>
          </div>
        </div>

        {(formData.device_type === 'firewall' || formData.device_type === 'router' || formData.device_type === 'firewall_router') && (
          <div className="border border-border rounded-lg p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Internet Connections</h2>
              <button
                type="button"
                onClick={addConnection}
                className="flex items-center gap-1 px-3 py-1 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
              >
                <Plus className="h-4 w-4" /> Add ISP
              </button>
            </div>

            {internetConnections.length === 0 ? (
              <p className="text-muted-foreground text-sm">No internet connections added. Click "Add ISP" to add one.</p>
            ) : (
              <div className="space-y-4">
                {internetConnections.map((conn, index) => (
                  <div key={index} className="border border-border rounded-md p-4 space-y-3 relative">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Connection {index + 1}</span>
                        {conn.is_primary && (
                          <span className="px-2 py-0.5 text-xs bg-green-500/20 text-green-400 rounded">Primary</span>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => removeConnection(index)}
                        className="p-1 text-destructive hover:bg-destructive/10 rounded"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium mb-1">Provider Name *</label>
                        <input
                          type="text"
                          value={conn.provider_name || ''}
                          onChange={(e) => updateConnection(index, 'provider_name', e.target.value)}
                          className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                          placeholder="e.g., Comcast, AT&T"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Connection Type</label>
                        <select
                          value={conn.connection_type || 'fiber'}
                          onChange={(e) => updateConnection(index, 'connection_type', e.target.value)}
                          className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                        >
                          <option value="fiber">Fiber</option>
                          <option value="cable">Cable</option>
                          <option value="dsl">DSL</option>
                          <option value="wireless">5G/Wireless</option>
                          <option value="satellite">Satellite</option>
                          <option value="other">Other</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <label className="block text-sm font-medium mb-1">Download (Mbps)</label>
                        <input
                          type="number"
                          value={conn.download_speed || 100}
                          onChange={(e) => updateConnection(index, 'download_speed', parseInt(e.target.value) || 0)}
                          className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                          min="0"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Upload (Mbps)</label>
                        <input
                          type="number"
                          value={conn.upload_speed || 100}
                          onChange={(e) => updateConnection(index, 'upload_speed', parseInt(e.target.value) || 0)}
                          className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                          min="0"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Account #</label>
                        <input
                          type="text"
                          value={conn.account_number || ''}
                          onChange={(e) => updateConnection(index, 'account_number', e.target.value)}
                          className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                          placeholder="Optional"
                        />
                      </div>
                    </div>

                    <div className="flex items-center gap-4">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={conn.is_primary || false}
                          onChange={(e) => updateConnection(index, 'is_primary', e.target.checked)}
                          className="rounded"
                        />
                        <span className="text-sm">Primary connection</span>
                      </label>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Legacy fields for backward compatibility */}
            <details className="text-sm">
              <summary className="cursor-pointer text-muted-foreground hover:text-foreground">Legacy ISP fields (deprecated)</summary>
              <div className="mt-3 space-y-3 pl-4 border-l-2 border-border">
                <div>
                  <label className="block text-sm font-medium mb-1">Internet Provider (legacy)</label>
                  <input
                    type="text"
                    value={formData.internet_provider}
                    onChange={(e) => setFormData({ ...formData, internet_provider: e.target.value })}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                    placeholder="e.g., Comcast, AT&T"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Internet Speed (legacy)</label>
                  <input
                    type="text"
                    value={formData.internet_speed}
                    onChange={(e) => setFormData({ ...formData, internet_speed: e.target.value })}
                    className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                    placeholder="e.g., 100/100 Mbps"
                  />
                </div>
              </div>
            </details>
          </div>
        )}

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Network Details</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">IP Address</label>
              <input
                type="text"
                value={formData.ip_address}
                onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 192.168.1.1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">MAC Address</label>
              <input
                type="text"
                value={formData.mac_address}
                onChange={(e) => setFormData({ ...formData, mac_address: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 00:1A:2B:3C:4D:5E"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Serial Number</label>
              <input
                type="text"
                value={formData.serial_number}
                onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Firmware Version</label>
              <input
                type="text"
                value={formData.firmware_version}
                onChange={(e) => setFormData({ ...formData, firmware_version: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Location</label>
            <select
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
            >
              <option value="">Select location (optional)</option>
              {locations.map((location) => (
                <option key={location.id} value={location.id}>
                  {location.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              rows={4}
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="rounded"
            />
            <label htmlFor="is_active" className="text-sm font-medium">
              Active
            </label>
          </div>
        </div>

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            {id ? 'Update' : 'Create'} Device
          </button>
          <button
            type="button"
            onClick={() => navigate('/endpoints')}
            className="px-6 py-2 border border-border rounded-md hover:bg-accent"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
