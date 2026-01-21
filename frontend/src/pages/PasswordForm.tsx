import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { passwordAPI } from '../services/core';
import { PasswordEntry, PasswordEntryVersion } from '../types/core';
import { ArrowLeft } from 'lucide-react';
import { useOrganization } from '../contexts/OrganizationContext';
import { VersionHistory } from '../components/VersionHistory';

export const PasswordForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id?: string }>();
  const { selectedOrg } = useOrganization();
  const isEditMode = !!id && id !== 'new';
  const [loading, setLoading] = useState(isEditMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({});
  const [formData, setFormData] = useState<Partial<PasswordEntry>>({
    name: '',
    username: '',
    password: '',
    url: '',
    notes: '',
    category: 'other',
  });

  useEffect(() => {
    if (isEditMode && id) {
      passwordAPI.getById(id).then(r => setFormData(r.data)).finally(() => setLoading(false)).catch(() => {});
    } else {
      // Set organization from context when creating new entry
      if (selectedOrg) {
        setFormData(prev => ({ ...prev, organization: selectedOrg.id }));
      }
      setLoading(false);
    }
  }, [id, isEditMode, selectedOrg]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (isEditMode && id) {
        await passwordAPI.update(id, formData);
        navigate(`/passwords/${id}`);
      } else {
        const response = await passwordAPI.create(formData);
        navigate(`/passwords/${response.data.id}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-4 mb-8">
        <Button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-700"><ArrowLeft className="w-5 h-5" /></Button>
        <h1 className="text-3xl font-bold text-foreground">{isEditMode ? 'Edit Password' : 'Add Password'}</h1>
      </div>

      <Card className="p-6">
        {error && <div className="mb-6 p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">Name *</label>
            <Input type="text" name="name" value={formData.name || ''} onChange={handleChange} placeholder="e.g., Company Mail Server" required className="bg-input border-input text-foreground" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Username</label>
              <Input type="text" name="username" value={formData.username || ''} onChange={handleChange} className="bg-input border-input text-foreground" />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">
                Password {!isEditMode && '*'}
              </label>
              <Input
                type="password"
                name="password"
                value={formData.password || ''}
                onChange={handleChange}
                required={!isEditMode}
                placeholder={isEditMode ? '(leave blank to keep existing)' : ''}
                className="bg-input border-input text-foreground"
              />
              {isEditMode && (
                <p className="text-xs text-muted-foreground mt-1">
                  Leave blank to keep the existing password
                </p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">URL</label>
            <Input type="url" name="url" value={formData.url || ''} onChange={handleChange} placeholder="https://example.com" className="bg-input border-input text-foreground" />
          </div>

          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">Category</label>
            <select name="category" value={formData.category || 'other'} onChange={handleChange} className="w-full px-4 py-2 bg-input border border-input rounded-lg text-foreground">
              <option value="account">Account</option>
              <option value="service">Service</option>
              <option value="device">Device</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">Notes</label>
            <textarea name="notes" value={formData.notes || ''} onChange={handleChange} rows={3} className="w-full px-4 py-2 bg-input border border-input rounded-lg text-foreground" />
          </div>

          <div className="flex gap-4 pt-6 border-t border-gray-700">
            <Button type="button" onClick={() => navigate(-1)} className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground">Cancel</Button>
            <Button type="submit" disabled={submitting} className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50">
              {submitting ? 'Saving...' : (isEditMode ? 'Update' : 'Add Password')}
            </Button>
          </div>
        </form>
      </Card>

      {isEditMode && id && (
        <Card className="p-6">
          <VersionHistory<PasswordEntryVersion>
            entryId={id}
            getVersions={passwordAPI.getVersions}
            restoreVersion={passwordAPI.restoreVersion}
            onRestore={() => {
              // Reload the form data after restore
              passwordAPI.getById(id).then(r => setFormData(r.data));
            }}
            renderVersionDetails={(version) => (
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium text-gray-400">Name:</span>
                  <span className="ml-2 text-gray-300">{version.name}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-400">Username:</span>
                  <span className="ml-2 text-gray-300">{version.username || '(none)'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-400">Password:</span>
                  <span className="ml-2 text-gray-300 font-mono">
                    {showPasswords[version.id] ? version.password : '•'.repeat(12)}
                  </span>
                  <button
                    onClick={() => setShowPasswords(prev => ({ ...prev, [version.id]: !prev[version.id] }))}
                    className="px-2 py-1 text-xs bg-secondary hover:bg-secondary/80 text-secondary-foreground rounded"
                  >
                    {showPasswords[version.id] ? 'Hide' : 'Show'}
                  </button>
                </div>
                <div>
                  <span className="font-medium text-gray-400">URL:</span>
                  <span className="ml-2 text-gray-300">{version.url || '(none)'}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-400">Category:</span>
                  <span className="ml-2 text-gray-300">{version.category}</span>
                </div>
                {version.notes && (
                  <div>
                    <span className="font-medium text-gray-400">Notes:</span>
                    <p className="mt-1 text-gray-300">{version.notes}</p>
                  </div>
                )}
              </div>
            )}
          />
        </Card>
      )}
    </div>
  );
};
