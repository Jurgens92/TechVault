import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { locationAPI } from '../services/core';
import { Location } from '../types/core';
import { ArrowLeft } from 'lucide-react';
import { useOrganization } from '../contexts/OrganizationContext';

export const LocationForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id?: string }>();
  const { selectedOrg } = useOrganization();
  const isEditMode = !!id && id !== 'new';

  const [loading, setLoading] = useState(isEditMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Partial<Location>>({
    name: '',
    description: '',
    address: '',
    city: '',
    state_province: '',
    postal_code: '',
    country: '',
    phone: '',
    is_active: true,
  });

  useEffect(() => {
    if (isEditMode && id) {
      fetchLocation();
    } else {
      // Set organization from context when creating new entry
      if (selectedOrg) {
        setFormData(prev => ({ ...prev, organization: selectedOrg.id }));
      }
    }
  }, [id, isEditMode, selectedOrg]);

  const fetchLocation = async () => {
    try {
      if (!id) return;
      const response = await locationAPI.getById(id);
      setFormData(response.data);
    } catch (err) {
      setError('Failed to load location');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      if (isEditMode && id) {
        await locationAPI.update(id, formData);
        navigate(`/locations/${id}`);
      } else {
        const response = await locationAPI.create(formData);
        navigate(`/locations/${response.data.id}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save location');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-4 mb-8">
        <Button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-700"><ArrowLeft className="w-5 h-5" /></Button>
        <h1 className="text-3xl font-bold text-foreground">{isEditMode ? 'Edit Location' : 'Create Location'}</h1>
      </div>

      <Card className="p-6">
        {error && <div className="mb-6 p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">Location Name *</label>
            <Input
              type="text"
              name="name"
              value={formData.name || ''}
              onChange={handleChange}
              placeholder="e.g., Main Office"
              required
              className="bg-input border-input text-foreground"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">Description</label>
            <textarea
              name="description"
              value={formData.description || ''}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 bg-input border border-input rounded-lg text-foreground"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">Street Address *</label>
            <Input
              type="text"
              name="address"
              value={formData.address || ''}
              onChange={handleChange}
              required
              className="bg-input border-input text-foreground"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">City *</label>
              <Input
                type="text"
                name="city"
                value={formData.city || ''}
                onChange={handleChange}
                required
                className="bg-input border-input text-foreground"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">State/Province</label>
              <Input
                type="text"
                name="state_province"
                value={formData.state_province || ''}
                onChange={handleChange}
                className="bg-input border-input text-foreground"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Postal Code *</label>
              <Input
                type="text"
                name="postal_code"
                value={formData.postal_code || ''}
                onChange={handleChange}
                required
                className="bg-input border-input text-foreground"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Country *</label>
              <Input
                type="text"
                name="country"
                value={formData.country || ''}
                onChange={handleChange}
                required
                className="bg-input border-input text-foreground"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-muted-foreground mb-2">Phone</label>
            <Input
              type="tel"
              name="phone"
              value={formData.phone || ''}
              onChange={handleChange}
              className="bg-input border-input text-foreground"
            />
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active || false}
              onChange={handleChange}
              className="w-4 h-4 rounded"
            />
            <label className="text-sm font-medium text-muted-foreground">Location is Active</label>
          </div>

          <div className="flex gap-4 pt-6 border-t border-gray-700">
            <Button type="button" onClick={() => navigate(-1)} className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground">Cancel</Button>
            <Button type="submit" disabled={submitting} className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50">
              {submitting ? 'Saving...' : (isEditMode ? 'Update Location' : 'Create Location')}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};
