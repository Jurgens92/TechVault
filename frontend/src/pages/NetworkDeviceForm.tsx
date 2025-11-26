import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOrganization } from '@/contexts/OrganizationContext';
import { networkDeviceAPI, locationAPI } from '@/services/core';
import type { NetworkDevice, Location } from '@/types/core';
import { ArrowLeft, Loader2 } from 'lucide-react';

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
      setLocations(response.data);
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
    } catch (error) {
      console.error('Failed to load device:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOrg) return;

    try {
      setLoading(true);
      const data = {
        ...formData,
        organization: selectedOrg.id,
        location: formData.location || null,
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
            <h2 className="text-lg font-semibold">Internet Connection</h2>

            <div>
              <label className="block text-sm font-medium mb-2">Internet Provider</label>
              <input
                type="text"
                value={formData.internet_provider}
                onChange={(e) => setFormData({ ...formData, internet_provider: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., Comcast, AT&T"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Internet Speed</label>
              <input
                type="text"
                value={formData.internet_speed}
                onChange={(e) => setFormData({ ...formData, internet_speed: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 100/100 Mbps"
              />
            </div>
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
