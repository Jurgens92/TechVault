import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOrganization } from '@/contexts/OrganizationContext';
import { endpointUserAPI, locationAPI, contactAPI } from '@/services/core';
import type { EndpointUser, Location, Contact } from '@/types/core';
import { ArrowLeft, Loader2 } from 'lucide-react';

export function EndpointUserForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState<Location[]>([]);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    device_type: 'desktop' as EndpointUser['device_type'],
    assigned_to: '',
    manufacturer: '',
    model: '',
    cpu: '',
    ram: '',
    storage: '',
    gpu: '',
    operating_system: '',
    software_installed: '',
    ip_address: '',
    mac_address: '',
    hostname: '',
    serial_number: '',
    purchase_date: '',
    warranty_expiry: '',
    location: '',
    notes: '',
    is_active: true,
  });

  useEffect(() => {
    if (selectedOrg) {
      loadData();
    }
    if (id) {
      loadEndpoint();
    }
  }, [id, selectedOrg]);

  const loadData = async () => {
    if (!selectedOrg) return;
    try {
      const [locationsRes, contactsRes] = await Promise.all([
        locationAPI.byOrganization(selectedOrg.id),
        contactAPI.byOrganization(selectedOrg.id),
      ]);
      // Sort locations by creation date (oldest first)
      const sortedLocations = locationsRes.data.sort((a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      setLocations(sortedLocations);
      setContacts(contactsRes.data);

      // If creating a new endpoint (not editing), pre-select the first location
      if (!id && sortedLocations.length > 0) {
        setFormData((prev) => ({ ...prev, location: sortedLocations[0].id }));
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const loadEndpoint = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await endpointUserAPI.getById(id);
      const endpoint = response.data;
      setFormData({
        name: endpoint.name,
        device_type: endpoint.device_type,
        assigned_to: endpoint.assigned_to || '',
        manufacturer: endpoint.manufacturer,
        model: endpoint.model,
        cpu: endpoint.cpu,
        ram: endpoint.ram,
        storage: endpoint.storage,
        gpu: endpoint.gpu,
        operating_system: endpoint.operating_system,
        software_installed: endpoint.software_installed,
        ip_address: endpoint.ip_address,
        mac_address: endpoint.mac_address,
        hostname: endpoint.hostname,
        serial_number: endpoint.serial_number,
        purchase_date: endpoint.purchase_date || '',
        warranty_expiry: endpoint.warranty_expiry || '',
        location: endpoint.location || '',
        notes: endpoint.notes,
        is_active: endpoint.is_active,
      });
    } catch (error) {
      console.error('Failed to load endpoint:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContactChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const contactId = e.target.value;

    // Find the selected contact
    const selectedContact = contacts.find(c => c.id === contactId);

    // Auto-sync location from contact, but allow manual override
    // Only update location if a contact is selected and they have a location
    if (selectedContact && selectedContact.location) {
      setFormData({
        ...formData,
        assigned_to: contactId,
        location: selectedContact.location
      });
    } else {
      // Just update assigned_to, keep current location
      setFormData({ ...formData, assigned_to: contactId });
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
        assigned_to: formData.assigned_to || null,
        location: formData.location || null,
        purchase_date: formData.purchase_date || null,
        warranty_expiry: formData.warranty_expiry || null,
      };

      if (id) {
        await endpointUserAPI.update(id, data);
      } else {
        await endpointUserAPI.create(data);
      }

      navigate('/endpoints?tab=users');
    } catch (error) {
      console.error('Failed to save endpoint:', error);
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
        {id ? 'Edit User Endpoint' : 'Add User Endpoint'}
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
              placeholder="e.g., DESK-001, LAPTOP-JOHN"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Device Type <span className="text-destructive">*</span>
            </label>
            <select
              value={formData.device_type}
              onChange={(e) => setFormData({ ...formData, device_type: e.target.value as EndpointUser['device_type'] })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
            >
              <option value="desktop">Desktop</option>
              <option value="laptop">Laptop</option>
              <option value="workstation">Workstation</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Assigned To
              <span className="text-xs text-muted-foreground ml-2">(auto-syncs location)</span>
            </label>
            <select
              value={formData.assigned_to}
              onChange={handleContactChange}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
            >
              <option value="">Select user (optional)</option>
              {contacts.map((contact) => (
                <option key={contact.id} value={contact.id}>
                  {contact.full_name} ({contact.email})
                </option>
              ))}
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
                placeholder="e.g., Dell, HP, Lenovo"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Model</label>
              <input
                type="text"
                value={formData.model}
                onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., OptiPlex 7090"
              />
            </div>
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Hardware Specifications</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">CPU</label>
              <input
                type="text"
                value={formData.cpu}
                onChange={(e) => setFormData({ ...formData, cpu: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., Intel Core i7-11700"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">RAM</label>
              <input
                type="text"
                value={formData.ram}
                onChange={(e) => setFormData({ ...formData, ram: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 16GB DDR4"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Storage</label>
              <input
                type="text"
                value={formData.storage}
                onChange={(e) => setFormData({ ...formData, storage: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 512GB SSD"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">GPU</label>
              <input
                type="text"
                value={formData.gpu}
                onChange={(e) => setFormData({ ...formData, gpu: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., NVIDIA RTX 3060"
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
              placeholder="e.g., Windows 11 Pro"
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
                placeholder="192.168.1.100"
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
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
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
              <label className="block text-sm font-medium mb-2">Purchase Date</label>
              <input
                type="date"
                value={formData.purchase_date}
                onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Warranty Expiry</label>
              <input
                type="date"
                value={formData.warranty_expiry}
                onChange={(e) => setFormData({ ...formData, warranty_expiry: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Location
              <span className="text-xs text-muted-foreground ml-2">(can override)</span>
            </label>
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
            {id ? 'Update' : 'Create'} Endpoint
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
