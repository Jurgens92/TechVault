import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { configurationAPI } from '../services/core';
import { Configuration, ConfigurationVersion } from '../types/core';
import { ArrowLeft } from 'lucide-react';
import { useOrganization } from '../contexts/OrganizationContext';
import { VersionHistory } from '../components/VersionHistory';

export const ConfigurationForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id?: string }>();
  const { selectedOrg } = useOrganization();
  const isEditMode = !!id && id !== 'new';
  const [loading, setLoading] = useState(isEditMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<Configuration>>({
    name: '',
    config_type: 'other',
    content: '',
    description: '',
    version: '',
    is_active: true,
  });

  useEffect(() => {
    if (isEditMode && id) {
      configurationAPI.getById(id).then(r => setFormData(r.data)).finally(() => setLoading(false)).catch(() => {});
    } else {
      // Set organization from context when creating new entry
      if (selectedOrg) {
        setFormData(prev => ({ ...prev, organization: selectedOrg.id }));
      }
      setLoading(false);
    }
  }, [id, isEditMode, selectedOrg]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (isEditMode && id) {
        await configurationAPI.update(id, formData);
        navigate(`/configurations/${id}`);
      } else {
        const response = await configurationAPI.create(formData);
        navigate(`/configurations/${response.data.id}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>;

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-4 mb-8">
        <Button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-700"><ArrowLeft className="w-5 h-5" /></Button>
        <h1 className="text-3xl font-bold text-white">{isEditMode ? 'Edit Configuration' : 'Create Configuration'}</h1>
      </div>

      <Card className="p-6">
        {error && <div className="mb-6 p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Configuration Name *</label>
            <Input type="text" name="name" value={formData.name || ''} onChange={handleChange} required className="bg-gray-700 border-gray-600 text-white" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Type *</label>
              <select name="config_type" value={formData.config_type || 'other'} onChange={handleChange} className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white">
                <option value="network">Network</option>
                <option value="server">Server</option>
                <option value="application">Application</option>
                <option value="security">Security</option>
                <option value="backup">Backup</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Version</label>
              <Input type="text" name="version" value={formData.version || ''} onChange={handleChange} placeholder="1.0.0" className="bg-gray-700 border-gray-600 text-white" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
            <textarea name="description" value={formData.description || ''} onChange={handleChange} rows={3} className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Configuration Content *</label>
            <textarea name="content" value={formData.content || ''} onChange={handleChange} required rows={10} className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white font-mono" />
          </div>

          <div className="flex items-center gap-3">
            <input type="checkbox" name="is_active" checked={formData.is_active || false} onChange={handleChange} className="w-4 h-4 rounded" />
            <label className="text-sm font-medium text-gray-300">Configuration is Active</label>
          </div>

          <div className="flex gap-4 pt-6 border-t border-gray-700">
            <Button type="button" onClick={() => navigate(-1)} className="flex-1 bg-gray-700 hover:bg-gray-600">Cancel</Button>
            <Button type="submit" disabled={submitting} className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50">
              {submitting ? 'Saving...' : (isEditMode ? 'Update' : 'Create')}
            </Button>
          </div>
        </form>
      </Card>

      {isEditMode && id && (
        <Card className="p-6">
          <VersionHistory<ConfigurationVersion>
            entryId={id}
            getVersions={configurationAPI.getVersions}
            restoreVersion={configurationAPI.restoreVersion}
            onRestore={() => {
              // Reload the form data after restore
              configurationAPI.getById(id).then(r => setFormData(r.data));
            }}
            renderVersionDetails={(version) => (
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium text-gray-400">Name:</span>
                  <span className="ml-2 text-gray-300">{version.name}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-400">Type:</span>
                  <span className="ml-2 text-gray-300">{version.config_type}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-400">Version:</span>
                  <span className="ml-2 text-gray-300">{version.version || '(none)'}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-400">Active:</span>
                  <span className="ml-2 text-gray-300">{version.is_active ? 'Yes' : 'No'}</span>
                </div>
                {version.description && (
                  <div>
                    <span className="font-medium text-gray-400">Description:</span>
                    <p className="mt-1 text-gray-300">{version.description}</p>
                  </div>
                )}
                <div>
                  <span className="font-medium text-gray-400">Content:</span>
                  <pre className="mt-1 p-2 bg-gray-800 rounded text-gray-300 whitespace-pre-wrap text-xs font-mono">
                    {version.content}
                  </pre>
                </div>
              </div>
            )}
          />
        </Card>
      )}
    </div>
  );
};
