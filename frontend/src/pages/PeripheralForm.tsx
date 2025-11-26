import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOrganization } from '@/contexts/OrganizationContext';
import { peripheralAPI, locationAPI } from '@/services/core';
import type { Peripheral, Location } from '@/types/core';
import { ArrowLeft, Loader2 } from 'lucide-react';

export function PeripheralForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState<Location[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    device_type: 'printer' as Peripheral['device_type'],
    manufacturer: '',
    model: '',
    ip_address: '',
    mac_address: '',
    serial_number: '',
    location: '',
    notes: '',
    is_active: true,
  });

  useEffect(() => {
    if (selectedOrg) {
      loadLocations();
    }
    if (id) {
      loadPeripheral();
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

  const loadPeripheral = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await peripheralAPI.getById(id);
      const peripheral = response.data;
      setFormData({
        name: peripheral.name,
        device_type: peripheral.device_type,
        manufacturer: peripheral.manufacturer,
        model: peripheral.model,
        ip_address: peripheral.ip_address,
        mac_address: peripheral.mac_address,
        serial_number: peripheral.serial_number,
        location: peripheral.location || '',
        notes: peripheral.notes,
        is_active: peripheral.is_active,
      });
    } catch (error) {
      console.error('Failed to load peripheral:', error);
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
        await peripheralAPI.update(id, data);
      } else {
        await peripheralAPI.create(data);
      }

      navigate('/endpoints?tab=peripherals');
    } catch (error) {
      console.error('Failed to save peripheral:', error);
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
        {id ? 'Edit Peripheral' : 'Add Peripheral'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          <div>
            <label className="block text-sm font-medium mb-2">
              Device Name <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
              placeholder="e.g., HP-PRINTER-01, Scanner-Office"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Device Type <span className="text-destructive">*</span>
            </label>
            <select
              value={formData.device_type}
              onChange={(e) => setFormData({ ...formData, device_type: e.target.value as Peripheral['device_type'] })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
            >
              <option value="printer">Printer</option>
              <option value="scanner">Scanner</option>
              <option value="multifunction">Multifunction Printer</option>
              <option value="ups">UPS (Uninterruptible Power Supply)</option>
              <option value="nas">NAS (Network Attached Storage)</option>
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
                placeholder="e.g., HP, Canon, Epson"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Model</label>
              <input
                type="text"
                value={formData.model}
                onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., LaserJet Pro M404n"
              />
            </div>
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Network & Device Details</h2>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">IP Address</label>
              <input
                type="text"
                value={formData.ip_address}
                onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="192.168.1.200"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">MAC Address</label>
              <input
                type="text"
                value={formData.mac_address}
                onChange={(e) => setFormData({ ...formData, mac_address: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Serial Number</label>
              <input
                type="text"
                value={formData.serial_number}
                onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
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
              placeholder="Additional information, maintenance schedule, toner details, etc."
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
            {id ? 'Update' : 'Create'} Peripheral
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
