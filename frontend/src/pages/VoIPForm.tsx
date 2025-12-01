import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOrganization } from '@/contexts/OrganizationContext';
import { voipAPI, contactAPI } from '@/services/core';
import type { VoIP, Contact } from '@/types/core';
import { ArrowLeft, Loader2, X } from 'lucide-react';

export function VoIPForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [loading, setLoading] = useState(false);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    voip_type: 'teams' as VoIP['voip_type'],
    assigned_contact_ids: [] as string[],
    license_key: '',
    version: '',
    license_type: 'subscription' as VoIP['license_type'],
    purchase_date: '',
    expiry_date: '',
    vendor: '',
    quantity: 1,
    phone_numbers: '',
    extensions: '',
    notes: '',
    is_active: true,
  });

  useEffect(() => {
    if (selectedOrg) {
      loadData();
    }
    if (id) {
      loadVoIP();
    }
  }, [id, selectedOrg]);

  const loadData = async () => {
    if (!selectedOrg) return;
    try {
      const contactsRes = await contactAPI.byOrganization(selectedOrg.id);
      setContacts(contactsRes.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const loadVoIP = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await voipAPI.getById(id);
      const voip = response.data;
      setFormData({
        name: voip.name,
        voip_type: voip.voip_type,
        assigned_contact_ids: voip.assigned_contacts?.map(a => a.contact_id) || [],
        license_key: voip.license_key,
        version: voip.version,
        license_type: voip.license_type,
        purchase_date: voip.purchase_date || '',
        expiry_date: voip.expiry_date || '',
        vendor: voip.vendor,
        quantity: voip.quantity,
        phone_numbers: voip.phone_numbers,
        extensions: voip.extensions,
        notes: voip.notes,
        is_active: voip.is_active,
      });
    } catch (error) {
      console.error('Failed to load VoIP:', error);
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
        purchase_date: formData.purchase_date || null,
        expiry_date: formData.expiry_date || null,
      };

      if (id) {
        await voipAPI.update(id, data);
      } else {
        await voipAPI.create(data);
      }

      navigate('/endpoints?tab=voip');
    } catch (error) {
      console.error('Failed to save VoIP:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddContact = (contactId: string) => {
    if (!formData.assigned_contact_ids.includes(contactId)) {
      setFormData({
        ...formData,
        assigned_contact_ids: [...formData.assigned_contact_ids, contactId],
      });
    }
    setSearchQuery('');
    setShowDropdown(false);
  };

  const handleRemoveContact = (contactId: string) => {
    setFormData({
      ...formData,
      assigned_contact_ids: formData.assigned_contact_ids.filter((id) => id !== contactId),
    });
  };

  const filteredContacts = contacts.filter(
    (contact) =>
      contact.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      contact.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const assignedContacts = contacts.filter((c) =>
    formData.assigned_contact_ids.includes(c.id)
  );

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
        onClick={() => navigate('/endpoints?tab=voip')}
        className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to VoIP
      </button>

      <h1 className="text-3xl font-bold mb-6">
        {id ? 'Edit VoIP Service' : 'Add VoIP Service'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          <div>
            <label className="block text-sm font-medium mb-2">
              Service Name <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
              placeholder="e.g., Microsoft Teams, Zoom Phone, RingCentral"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              VoIP Type <span className="text-destructive">*</span>
            </label>
            <select
              value={formData.voip_type}
              onChange={(e) => setFormData({ ...formData, voip_type: e.target.value as VoIP['voip_type'] })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
            >
              <option value="teams">Microsoft Teams</option>
              <option value="3cx">3CX</option>
              <option value="yeastar">Yeastar</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Assign To Users</label>
            <div className="relative">
              <div
                className="w-full px-3 py-2 border border-input rounded-md bg-background min-h-[42px] cursor-pointer flex items-center justify-between"
                onClick={() => setShowDropdown(!showDropdown)}
              >
                <div className="flex flex-wrap gap-2">
                  {assignedContacts.length > 0 ? (
                    assignedContacts.map((contact) => (
                      <div
                        key={contact.id}
                        className="flex items-center gap-1 bg-primary/20 text-primary px-2 py-1 rounded text-sm"
                      >
                        <span>{contact.full_name}</span>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRemoveContact(contact.id);
                          }}
                          className="hover:text-primary/80"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </div>
                    ))
                  ) : (
                    <span className="text-muted-foreground">Select users (optional)</span>
                  )}
                </div>
              </div>

              {showDropdown && (
                <div className="absolute z-50 w-full mt-1 bg-background border border-input rounded-md shadow-lg">
                  <div className="p-2 border-b border-border">
                    <input
                      type="text"
                      className="w-full px-2 py-1 text-sm bg-background border border-input rounded focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Search users..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                  <div className="max-h-60 overflow-y-auto">
                    {filteredContacts.length === 0 ? (
                      <div className="px-3 py-2 text-sm text-muted-foreground text-center">
                        No users found
                      </div>
                    ) : (
                      filteredContacts.map((contact) => (
                        <div
                          key={contact.id}
                          className={`px-3 py-2 text-sm cursor-pointer flex items-center justify-between hover:bg-accent ${
                            formData.assigned_contact_ids.includes(contact.id) ? 'bg-primary/10' : ''
                          }`}
                          onClick={() => handleAddContact(contact.id)}
                        >
                          <div>
                            <p className="font-medium">{contact.full_name}</p>
                            <p className="text-xs text-muted-foreground">{contact.email}</p>
                          </div>
                          {formData.assigned_contact_ids.includes(contact.id) && (
                            <span className="text-primary">✓</span>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Vendor</label>
              <input
                type="text"
                value={formData.vendor}
                onChange={(e) => setFormData({ ...formData, vendor: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., Microsoft, Zoom, RingCentral"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Version/Plan</label>
              <input
                type="text"
                value={formData.version}
                onChange={(e) => setFormData({ ...formData, version: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., Business, Enterprise, Pro"
              />
            </div>
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">License Information</h2>

          <div>
            <label className="block text-sm font-medium mb-2">License Key / Account ID</label>
            <input
              type="text"
              value={formData.license_key}
              onChange={(e) => setFormData({ ...formData, license_key: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              placeholder="Account ID or license code"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              License Type <span className="text-destructive">*</span>
            </label>
            <select
              value={formData.license_type}
              onChange={(e) => setFormData({ ...formData, license_type: e.target.value as VoIP['license_type'] })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
            >
              <option value="perpetual">Perpetual</option>
              <option value="subscription">Subscription</option>
              <option value="trial">Trial</option>
              <option value="free">Free</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
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
              <label className="block text-sm font-medium mb-2">Expiry Date</label>
              <input
                type="date"
                value={formData.expiry_date}
                onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Quantity (Licenses)</label>
            <input
              type="number"
              value={formData.quantity}
              onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) || 1 })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              min="1"
            />
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">VoIP Details</h2>

          <div>
            <label className="block text-sm font-medium mb-2">Phone Numbers</label>
            <input
              type="text"
              value={formData.phone_numbers}
              onChange={(e) => setFormData({ ...formData, phone_numbers: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              placeholder="Comma-separated phone numbers (e.g., +1-555-0100, +1-555-0200)"
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Enter multiple phone numbers separated by commas
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Extensions</label>
            <input
              type="text"
              value={formData.extensions}
              onChange={(e) => setFormData({ ...formData, extensions: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              placeholder="Comma-separated extensions (e.g., 100, 101, 102)"
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Enter multiple extensions separated by commas
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              rows={3}
              placeholder="Any additional notes about this VoIP service"
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
            {id ? 'Update' : 'Create'} VoIP Service
          </button>
          <button
            type="button"
            onClick={() => navigate('/endpoints?tab=voip')}
            className="px-6 py-2 border border-border rounded-md hover:bg-accent"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
