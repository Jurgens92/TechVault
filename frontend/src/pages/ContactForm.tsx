import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { contactAPI, locationAPI } from '../services/core';
import { Contact, Location } from '../types/core';
import { ArrowLeft } from 'lucide-react';
import { useOrganization } from '../contexts/OrganizationContext';

export const ContactForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id?: string }>();
  const { selectedOrg } = useOrganization();
  const isEditMode = !!id && id !== 'new';

  const [loading, setLoading] = useState(isEditMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [formData, setFormData] = useState<Partial<Contact>>({
    first_name: '',
    last_name: '',
    title: '',
    email: '',
    phone: '',
    mobile: '',
    location: '',
    notes: '',
    is_active: true,
  });

  useEffect(() => {
    if (selectedOrg) {
      loadLocations();
    }
  }, [selectedOrg]);

  useEffect(() => {
    if (isEditMode && id) {
      contactAPI.getById(id).then(r => setFormData(r.data)).finally(() => setLoading(false)).catch(() => {});
    } else {
      // Set organization from context when creating new entry
      if (selectedOrg) {
        setFormData(prev => ({ ...prev, organization: selectedOrg.id }));
      }
      setLoading(false);
    }
  }, [id, isEditMode, selectedOrg]);

  const loadLocations = async () => {
    if (!selectedOrg) return;
    try {
      const response = await locationAPI.byOrganization(selectedOrg.id);
      // Sort by creation date (oldest first)
      const sortedLocations = response.data.sort((a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      setLocations(sortedLocations);

      // If creating a new contact (not editing), pre-select the first location
      if (!id && sortedLocations.length > 0) {
        setFormData((prev) => ({ ...prev, location: sortedLocations[0].id }));
      }
    } catch (error) {
      console.error('Failed to load locations:', error);
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
    try {
      // Convert empty location to null
      const submitData = {
        ...formData,
        location: formData.location || null,
      };

      if (isEditMode && id) {
        await contactAPI.update(id, submitData);
        navigate(`/contacts/${id}`);
      } else {
        const response = await contactAPI.create(submitData);
        navigate(`/contacts/${response.data.id}`);
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
        <h1 className="text-3xl font-bold text-foreground">{isEditMode ? 'Edit Contact' : 'Create Contact'}</h1>
      </div>

      <Card className="p-6">
        {error && <div className="mb-6 p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">First Name *</label>
              <Input type="text" name="first_name" value={formData.first_name || ''} onChange={handleChange} required className="bg-input border-input text-foreground" />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Last Name *</label>
              <Input type="text" name="last_name" value={formData.last_name || ''} onChange={handleChange} required className="bg-input border-input text-foreground" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Title</label>
              <Input type="text" name="title" value={formData.title || ''} onChange={handleChange} className="bg-input border-input text-foreground" />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Location / Site</label>
              <select
                name="location"
                value={formData.location || ''}
                onChange={handleChange}
                className="w-full px-3 py-2 bg-input border border-input rounded-md text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">No location assigned</option>
                {locations.map((location) => (
                  <option key={location.id} value={location.id}>
                    {location.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Email *</label>
              <Input type="email" name="email" value={formData.email || ''} onChange={handleChange} required className="bg-input border-input text-foreground" />
            </div>
            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">Phone</label>
              <Input type="tel" name="phone" value={formData.phone || ''} onChange={handleChange} className="bg-input border-input text-foreground" />
            </div>
          </div>

          <div className="flex gap-4 pt-6 border-t border-gray-700">
            <Button type="button" onClick={() => navigate(-1)} className="flex-1 bg-secondary hover:bg-secondary/80 text-secondary-foreground">Cancel</Button>
            <Button type="submit" disabled={submitting} className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50">
              {submitting ? 'Saving...' : (isEditMode ? 'Update' : 'Create')}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};
