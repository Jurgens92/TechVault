import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { documentationAPI } from '../services/core';
import { Documentation, DocumentationVersion } from '../types/core';
import { ArrowLeft } from 'lucide-react';
import { useOrganization } from '../contexts/OrganizationContext';
import { useChoices } from '../contexts/ChoicesContext';
import { VersionHistory } from '../components/VersionHistory';

export const DocumentationForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id?: string }>();
  const { selectedOrg } = useOrganization();
  const { getChoicesForField, getChoiceLabel } = useChoices();
  const isEditMode = !!id && id !== 'new';
  const [loading, setLoading] = useState(isEditMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<Documentation>>({
    title: '',
    content: '',
    category: 'other',
    tags: '',
    is_published: false,
  });

  useEffect(() => {
    if (isEditMode && id) {
      documentationAPI.getById(id).then(r => setFormData(r.data)).finally(() => setLoading(false)).catch(() => {});
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
        await documentationAPI.update(id, formData);
        navigate(`/documentations/${id}`);
      } else {
        const response = await documentationAPI.create(formData);
        navigate(`/documentations/${response.data.id}`);
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
        <h1 className="text-3xl font-bold text-white">{isEditMode ? 'Edit Documentation' : 'Create Documentation'}</h1>
      </div>

      <Card className="p-6">
        {error && <div className="mb-6 p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Title *</label>
            <Input type="text" name="title" value={formData.title || ''} onChange={handleChange} required className="bg-gray-700 border-gray-600 text-white" />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Content *</label>
            <textarea name="content" value={formData.content || ''} onChange={handleChange} required rows={10} className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
              <select name="category" value={formData.category || 'other'} onChange={handleChange} className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white">
                {/* Single Source of Truth: Options fetched from /api/meta/choices/ */}
                {getChoicesForField('documentation_category').map(choice => (
                  <option key={choice.value} value={choice.value}>{choice.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Tags</label>
              <Input type="text" name="tags" value={formData.tags || ''} onChange={handleChange} placeholder="comma, separated, tags" className="bg-gray-700 border-gray-600 text-white" />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input type="checkbox" name="is_published" checked={formData.is_published || false} onChange={handleChange} className="w-4 h-4 rounded" />
            <label className="text-sm font-medium text-gray-300">Publish this documentation</label>
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
          <VersionHistory<DocumentationVersion>
            entryId={id}
            getVersions={documentationAPI.getVersions}
            restoreVersion={documentationAPI.restoreVersion}
            onRestore={() => {
              // Reload the form data after restore
              documentationAPI.getById(id).then(r => setFormData(r.data));
            }}
            renderVersionDetails={(version) => (
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-medium text-gray-400">Title:</span>
                  <span className="ml-2 text-gray-300">{version.title}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-400">Category:</span>
                  <span className="ml-2 text-gray-300">{getChoiceLabel('documentation_category', version.category)}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-400">Published:</span>
                  <span className="ml-2 text-gray-300">{version.is_published ? 'Yes' : 'No'}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-400">Content:</span>
                  <pre className="mt-1 p-2 bg-gray-800 rounded text-gray-300 whitespace-pre-wrap text-xs">
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
