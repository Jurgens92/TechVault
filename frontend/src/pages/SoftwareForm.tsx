import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOrganization } from '@/contexts/OrganizationContext';
import { softwareAPI, contactAPI } from '@/services/core';
import type { Software, Contact } from '@/types/core';
import { ArrowLeft, Loader2, X } from 'lucide-react';

interface SoftwareFormProps {
  editId?: string;
  onSave?: () => void;
  onCancel?: () => void;
  isModal?: boolean;
}

export function SoftwareForm({ editId, onSave, onCancel, isModal }: SoftwareFormProps = {}) {
  const { id: paramId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const id = editId ?? paramId;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    software_type: 'microsoft365' as Software['software_type'],
    assigned_contact_ids: [] as string[],
    license_key: '',
    version: '',
    license_type: 'perpetual' as Software['license_type'],
    purchase_date: '',
    expiry_date: '',
    vendor: '',
    quantity: 1,
    notes: '',
    is_active: true,
  });

  useEffect(() => {
    if (selectedOrg) {
      loadData();
    }
    if (id) {
      loadSoftware();
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

  const loadSoftware = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await softwareAPI.getById(id);
      const software = response.data;
      setFormData({
        name: software.name,
        software_type: software.software_type,
        assigned_contact_ids: software.assigned_contacts?.map(a => a.contact_id) || [],
        license_key: software.license_key,
        version: software.version,
        license_type: software.license_type,
        purchase_date: software.purchase_date || '',
        expiry_date: software.expiry_date || '',
        vendor: software.vendor,
        quantity: software.quantity,
        notes: software.notes,
        is_active: software.is_active,
      });
    } catch (error) {
      console.error('Failed to load software:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOrg) return;

    if (formData.assigned_contact_ids.length > formData.quantity) {
      setError(
        `Cannot save: ${formData.assigned_contact_ids.length} users are assigned but only ${formData.quantity} license(s) available. Remove ${formData.assigned_contact_ids.length - formData.quantity} user(s) or increase the license quantity.`
      );
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = {
        ...formData,
        organization: selectedOrg.id,
        purchase_date: formData.purchase_date || null,
        expiry_date: formData.expiry_date || null,
      };

      if (id) {
        await softwareAPI.update(id, data);
      } else {
        await softwareAPI.create(data);
      }

      if (onSave) {
        onSave();
      } else {
        navigate('/endpoints?tab=software');
      }
    } catch (err: unknown) {
      console.error('Failed to save software:', err);
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { data?: Record<string, unknown> } };
        const data = axiosErr.response?.data;
        if (data) {
          const messages = Object.entries(data)
            .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(', ') : val}`)
            .join('. ');
          setError(messages);
        } else {
          setError('Failed to save software. Please try again.');
        }
      } else {
        setError('Failed to save software. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddContact = (contactId: string) => {
    if (!formData.assigned_contact_ids.includes(contactId)) {
      if (formData.assigned_contact_ids.length >= formData.quantity) {
        return;
      }
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
    <div className={isModal ? 'space-y-6' : 'p-6 max-w-3xl'}>
      {!isModal && (
        <button
          onClick={() => navigate('/endpoints?tab=software')}
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Software
        </button>
      )}

      <h1 className={isModal ? 'text-xl font-bold mb-4' : 'text-3xl font-bold mb-6'}>
        {id ? 'Edit Software' : 'Add Software'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          <div>
            <label className="block text-sm font-medium mb-2">
              Software Name <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
              placeholder="e.g., Microsoft Office 365, AutoCAD, Exchange Online"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Software Type <span className="text-destructive">*</span>
            </label>
            <select
              value={formData.software_type}
              onChange={(e) => setFormData({ ...formData, software_type: e.target.value as Software['software_type'] })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
            >
              <option value="microsoft365">Microsoft 365</option>
              <option value="endpoint_protection">Endpoint Protection</option>
              <option value="design">Design/CAD</option>
              <option value="development">Development</option>
              <option value="subscription">Subscription Service</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Assign To Users
              <span className="text-muted-foreground font-normal ml-2">
                ({formData.assigned_contact_ids.length}/{formData.quantity} licenses used)
              </span>
            </label>
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
                      filteredContacts.map((contact) => {
                        const isAssigned = formData.assigned_contact_ids.includes(contact.id);
                        const atCapacity = !isAssigned && formData.assigned_contact_ids.length >= formData.quantity;
                        return (
                        <div
                          key={contact.id}
                          className={`px-3 py-2 text-sm flex items-center justify-between ${
                            isAssigned ? 'bg-primary/10 cursor-pointer hover:bg-accent' : atCapacity ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:bg-accent'
                          }`}
                          onClick={() => !atCapacity && handleAddContact(contact.id)}
                        >
                          <div>
                            <p className="font-medium">{contact.full_name}</p>
                            <p className="text-xs text-muted-foreground">{contact.email}</p>
                          </div>
                          {isAssigned && (
                            <span className="text-primary">✓</span>
                          )}
                          {atCapacity && (
                            <span className="text-xs text-muted-foreground">No licenses available</span>
                          )}
                        </div>
                        );
                      })
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
                placeholder="e.g., Microsoft, Autodesk, Adobe"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Version</label>
              <input
                type="text"
                value={formData.version}
                onChange={(e) => setFormData({ ...formData, version: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 2024, Pro, Standard, Plan 1"
              />
            </div>
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">License Information</h2>

          <div>
            <label className="block text-sm font-medium mb-2">License Key</label>
            <input
              type="text"
              value={formData.license_key}
              onChange={(e) => setFormData({ ...formData, license_key: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              placeholder="Product key or license code"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              License Type <span className="text-destructive">*</span>
            </label>
            <select
              value={formData.license_type}
              onChange={(e) => setFormData({ ...formData, license_type: e.target.value as Software['license_type'] })}
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

          <div className="grid grid-cols-3 gap-4">
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
            <div>
              <label className="block text-sm font-medium mb-2">Quantity</label>
              <input
                type="number"
                value={formData.quantity}
                onChange={(e) => {
                  const newQuantity = parseInt(e.target.value) || 1;
                  setFormData({ ...formData, quantity: newQuantity });
                  if (formData.assigned_contact_ids.length > newQuantity) {
                    setError(
                      `${formData.assigned_contact_ids.length} users are currently assigned. Remove ${formData.assigned_contact_ids.length - newQuantity} user(s) before reducing to ${newQuantity} license(s).`
                    );
                  } else {
                    setError(null);
                  }
                }}
                className={`w-full px-3 py-2 border rounded-md bg-background ${formData.assigned_contact_ids.length > formData.quantity ? 'border-destructive' : 'border-input'}`}
                min="1"
              />
              {formData.assigned_contact_ids.length > formData.quantity && (
                <p className="mt-1 text-xs text-destructive">
                  {formData.assigned_contact_ids.length} users assigned, exceeds {formData.quantity} license(s)
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Additional Details</h2>

          <div>
            <label className="block text-sm font-medium mb-2">Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              rows={3}
              placeholder="Any additional notes about this software"
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

        {error && (
          <div className="p-4 border border-destructive/50 bg-destructive/10 rounded-lg">
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading || formData.assigned_contact_ids.length > formData.quantity}
            className="flex items-center gap-2 px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
          >
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
            {id ? 'Update' : 'Create'} Software
          </button>
          <button
            type="button"
            onClick={() => onCancel ? onCancel() : navigate('/endpoints?tab=software')}
            className="px-6 py-2 border border-border rounded-md hover:bg-accent"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
