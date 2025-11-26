import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOrganization } from '@/contexts/OrganizationContext';
import { serverAPI, locationAPI } from '@/services/core';
import type { Server, Location } from '@/types/core';
import { ArrowLeft, Loader2 } from 'lucide-react';

export function ServerForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState<Location[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    server_type: 'physical' as Server['server_type'],
    role: '',
    manufacturer: '',
    model: '',
    cpu: '',
    ram: '',
    storage: '',
    operating_system: '',
    software_installed: '',
    ip_address: '',
    mac_address: '',
    hostname: '',
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
      loadServer();
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

  const loadServer = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await serverAPI.getById(id);
      const server = response.data;
      setFormData({
        name: server.name,
        server_type: server.server_type,
        role: server.role,
        manufacturer: server.manufacturer,
        model: server.model,
        cpu: server.cpu,
        ram: server.ram,
        storage: server.storage,
        operating_system: server.operating_system,
        software_installed: server.software_installed,
        ip_address: server.ip_address,
        mac_address: server.mac_address,
        hostname: server.hostname,
        serial_number: server.serial_number,
        location: server.location || '',
        notes: server.notes,
        is_active: server.is_active,
      });
    } catch (error) {
      console.error('Failed to load server:', error);
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
        await serverAPI.update(id, data);
      } else {
        await serverAPI.create(data);
      }

      navigate('/endpoints?tab=servers');
    } catch (error) {
      console.error('Failed to save server:', error);
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
        {id ? 'Edit Server' : 'Add Server'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          <div>
            <label className="block text-sm font-medium mb-2">
              Server Name <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
              placeholder="e.g., WEB-SERVER-01, DB-PROD"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Server Type <span className="text-destructive">*</span>
              </label>
              <select
                value={formData.server_type}
                onChange={(e) => setFormData({ ...formData, server_type: e.target.value as Server['server_type'] })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                required
              >
                <option value="physical">Physical Server</option>
                <option value="virtual">Virtual Machine</option>
                <option value="cloud">Cloud Instance</option>
                <option value="container">Container</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Role/Purpose</label>
              <input
                type="text"
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., Web Server, Database, File Server"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Manufacturer</label>
              <input
                type="text"
                value={formData.manufacturer}
                onChange={(e) => setFormData({ ...formData, manufacturer: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., Dell, HP, AWS"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Model</label>
              <input
                type="text"
                value={formData.model}
                onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., PowerEdge R740, EC2 t3.large"
              />
            </div>
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Hardware Specifications</h2>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">CPU</label>
              <input
                type="text"
                value={formData.cpu}
                onChange={(e) => setFormData({ ...formData, cpu: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 2x Xeon Gold 6248"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">RAM</label>
              <input
                type="text"
                value={formData.ram}
                onChange={(e) => setFormData({ ...formData, ram: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 64GB DDR4 ECC"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Storage</label>
              <input
                type="text"
                value={formData.storage}
                onChange={(e) => setFormData({ ...formData, storage: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 2TB SSD RAID 10"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Operating System</label>
            <input
              type="text"
              value={formData.operating_system}
              onChange={(e) => setFormData({ ...formData, operating_system: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              placeholder="e.g., Ubuntu 22.04 LTS, Windows Server 2022"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Installed Software/Services</label>
            <textarea
              value={formData.software_installed}
              onChange={(e) => setFormData({ ...formData, software_installed: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              rows={3}
              placeholder="Comma-separated list: Apache, MySQL, Docker, etc."
            />
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Network & Other Details</h2>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">IP Address</label>
              <input
                type="text"
                value={formData.ip_address}
                onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="10.0.1.50"
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
              <label className="block text-sm font-medium mb-2">Hostname</label>
              <input
                type="text"
                value={formData.hostname}
                onChange={(e) => setFormData({ ...formData, hostname: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="web-server-01.domain.com"
              />
            </div>
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
              rows={3}
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
            {id ? 'Update' : 'Create'} Server
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
