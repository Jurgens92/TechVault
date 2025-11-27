import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useOrganization } from '@/contexts/OrganizationContext';
import { backupAPI, locationAPI } from '@/services/core';
import type { Backup, Location } from '@/types/core';
import { ArrowLeft, Loader2 } from 'lucide-react';

export function BackupForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState<Location[]>([]);
  const [formData, setFormData] = useState({
    name: '',
    backup_type: 'server' as Backup['backup_type'],
    vendor: '',
    frequency: '',
    retention_period: '',
    storage_location: '',
    storage_capacity: '',
    target_systems: '',
    last_backup_date: '',
    next_backup_date: '',
    backup_status: 'active' as Backup['backup_status'],
    location: '',
    notes: '',
    is_active: true,
  });

  useEffect(() => {
    if (selectedOrg) {
      loadData();
    }
    if (id) {
      loadBackup();
    }
  }, [id, selectedOrg]);

  const loadData = async () => {
    if (!selectedOrg) return;
    try {
      const locationsRes = await locationAPI.byOrganization(selectedOrg.id);
      setLocations(locationsRes.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const loadBackup = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const response = await backupAPI.getById(id);
      const backup = response.data;

      // Format datetime values to work with datetime-local input
      const formatDateTimeLocal = (dateString: string | null) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        // Format as YYYY-MM-DDTHH:MM for datetime-local input
        return date.toISOString().slice(0, 16);
      };

      setFormData({
        name: backup.name,
        backup_type: backup.backup_type,
        vendor: backup.vendor,
        frequency: backup.frequency,
        retention_period: backup.retention_period,
        storage_location: backup.storage_location,
        storage_capacity: backup.storage_capacity,
        target_systems: backup.target_systems,
        last_backup_date: formatDateTimeLocal(backup.last_backup_date),
        next_backup_date: formatDateTimeLocal(backup.next_backup_date),
        backup_status: backup.backup_status,
        location: backup.location || '',
        notes: backup.notes,
        is_active: backup.is_active,
      });
    } catch (error) {
      console.error('Failed to load backup:', error);
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
        last_backup_date: formData.last_backup_date || null,
        next_backup_date: formData.next_backup_date || null,
      };

      if (id) {
        await backupAPI.update(id, data);
      } else {
        await backupAPI.create(data);
      }

      navigate('/endpoints?tab=backups');
    } catch (error) {
      console.error('Failed to save backup:', error);
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
        onClick={() => navigate('/endpoints?tab=backups')}
        className="flex items-center gap-2 text-muted-foreground hover:text-foreground mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Backups
      </button>

      <h1 className="text-3xl font-bold mb-6">
        {id ? 'Edit Backup' : 'Add Backup'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          <div>
            <label className="block text-sm font-medium mb-2">
              Backup Name <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
              placeholder="e.g., Veeam Server Backup, M365 Backup, Synology NAS"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Backup Type <span className="text-destructive">*</span>
            </label>
            <select
              value={formData.backup_type}
              onChange={(e) => setFormData({ ...formData, backup_type: e.target.value as Backup['backup_type'] })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
            >
              <option value="server">Server Backup</option>
              <option value="microsoft365">Microsoft 365 Backup</option>
              <option value="cloud">Cloud Backup</option>
              <option value="endpoint">Endpoint Backup</option>
              <option value="database">Database Backup</option>
              <option value="nas">NAS Backup</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Vendor</label>
              <input
                type="text"
                value={formData.vendor}
                onChange={(e) => setFormData({ ...formData, vendor: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., Veeam, Acronis, Datto, Backblaze"
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
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Backup Configuration</h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Frequency</label>
              <input
                type="text"
                value={formData.frequency}
                onChange={(e) => setFormData({ ...formData, frequency: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., Daily, Hourly, Weekly"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Retention Period</label>
              <input
                type="text"
                value={formData.retention_period}
                onChange={(e) => setFormData({ ...formData, retention_period: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 30 days, 1 year, 7 years"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Storage Location</label>
              <input
                type="text"
                value={formData.storage_location}
                onChange={(e) => setFormData({ ...formData, storage_location: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., AWS S3, On-premises NAS, Azure Blob"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Storage Capacity</label>
              <input
                type="text"
                value={formData.storage_capacity}
                onChange={(e) => setFormData({ ...formData, storage_capacity: e.target.value })}
                className="w-full px-3 py-2 border border-input rounded-md bg-background"
                placeholder="e.g., 500GB, 2TB, 10TB"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Target Systems</label>
            <textarea
              value={formData.target_systems}
              onChange={(e) => setFormData({ ...formData, target_systems: e.target.value })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              rows={3}
              placeholder="Describe what systems or data are being backed up"
            />
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Status & Monitoring</h2>

          <div>
            <label className="block text-sm font-medium mb-2">
              Backup Status <span className="text-destructive">*</span>
            </label>
            <select
              value={formData.backup_status}
              onChange={(e) => setFormData({ ...formData, backup_status: e.target.value as Backup['backup_status'] })}
              className="w-full px-3 py-2 border border-input rounded-md bg-background"
              required
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="failed">Failed</option>
              <option value="warning">Warning</option>
            </select>
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
              placeholder="Any additional notes about this backup solution"
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
            {id ? 'Update' : 'Create'} Backup
          </button>
          <button
            type="button"
            onClick={() => navigate('/endpoints?tab=backups')}
            className="px-6 py-2 border border-border rounded-md hover:bg-accent"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
