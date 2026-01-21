import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { organizationAPI } from '../services/core';
import { Organization } from '../types/core';
import { ArrowLeft, Edit, Trash2, MapPin, Mail, Phone, Globe, Building2 } from 'lucide-react';

export const OrganizationDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      fetchOrganization();
    }
  }, [id]);

  const fetchOrganization = async () => {
    try {
      if (!id) return;
      const [orgResponse, statsResponse] = await Promise.all([
        organizationAPI.getById(id),
        organizationAPI.getStats(id),
      ]);
      setOrganization(orgResponse.data);
      setStats(statsResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to load organization');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this organization? This action cannot be undone.')) {
      try {
        if (!id) return;
        await organizationAPI.delete(id);
        navigate('/organizations');
      } catch (err) {
        setError('Failed to delete organization');
        console.error(err);
      }
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <p className="mt-4 text-gray-400">Loading...</p>
      </div>
    );
  }

  if (!organization) {
    return (
      <Card className="p-8 text-center">
        <p className="text-gray-400">Organization not found</p>
        <Button
          onClick={() => navigate('/organizations')}
          className="mt-4 bg-blue-600 hover:bg-blue-700"
        >
          Back to Organizations
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div className="flex items-center gap-4">
          <Button
            onClick={() => navigate('/organizations')}
            className="p-2 hover:bg-gray-700 text-gray-300"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-3xl font-bold text-foreground">{organization.name}</h1>
          {!organization.is_active && (
            <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">Inactive</span>
          )}
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => navigate(`/organizations/${id}/edit`)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
          >
            <Edit className="w-4 h-4" />
            Edit
          </Button>
          <Button
            onClick={handleDelete}
            className="p-2 hover:bg-red-900/20 text-red-400"
          >
            <Trash2 className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">
          {error}
        </div>
      )}

      {/* Description */}
      {organization.description && (
        <Card className="p-6">
          <p className="text-gray-300">{organization.description}</p>
        </Card>
      )}

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-400">{stats.locations_count}</div>
            <div className="text-sm text-gray-400 mt-1">Locations</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-green-400">{stats.contacts_count}</div>
            <div className="text-sm text-gray-400 mt-1">Contacts</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-400">{stats.documentations_count}</div>
            <div className="text-sm text-gray-400 mt-1">Documentation</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-400">{stats.password_entries_count}</div>
            <div className="text-sm text-gray-400 mt-1">Passwords</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-2xl font-bold text-red-400">{stats.configurations_count}</div>
            <div className="text-sm text-gray-400 mt-1">Configurations</div>
          </Card>
        </div>
      )}

      {/* Contact Information */}
      <Card className="p-6 space-y-4">
        <h2 className="text-xl font-semibold text-foreground mb-4">Contact Information</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {organization.email && (
            <div className="flex items-start gap-3">
              <Mail className="w-5 h-5 text-blue-500 mt-1" />
              <div>
                <div className="text-sm text-gray-400">Email</div>
                <a href={`mailto:${organization.email}`} className="text-foreground hover:text-primary">
                  {organization.email}
                </a>
              </div>
            </div>
          )}
          {organization.phone && (
            <div className="flex items-start gap-3">
              <Phone className="w-5 h-5 text-green-500 mt-1" />
              <div>
                <div className="text-sm text-gray-400">Phone</div>
                <a href={`tel:${organization.phone}`} className="text-foreground hover:text-primary">
                  {organization.phone}
                </a>
              </div>
            </div>
          )}
          {organization.website && (
            <div className="flex items-start gap-3">
              <Globe className="w-5 h-5 text-purple-500 mt-1" />
              <div>
                <div className="text-sm text-gray-400">Website</div>
                <a href={organization.website} target="_blank" rel="noopener noreferrer" className="text-foreground hover:text-primary">
                  {organization.website}
                </a>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Address */}
      {(organization.address || organization.city || organization.country) && (
        <Card className="p-6 space-y-4">
          <h2 className="text-xl font-semibold text-foreground mb-4">Address</h2>
          <div className="flex items-start gap-3">
            <MapPin className="w-5 h-5 text-red-500 mt-1" />
            <div className="text-gray-300">
              {organization.address && <div>{organization.address}</div>}
              <div>
                {organization.city && <span>{organization.city}</span>}
                {organization.state_province && <span>, {organization.state_province}</span>}
                {organization.postal_code && <span> {organization.postal_code}</span>}
              </div>
              {organization.country && <div>{organization.country}</div>}
            </div>
          </div>
        </Card>
      )}

      {/* Related Items */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4">Related Items</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <Button
            onClick={() => navigate(`/locations?org=${id}`)}
            className="bg-gray-700 hover:bg-gray-600 text-white text-left h-auto py-4 px-4 flex flex-col"
          >
            <span className="font-semibold">Locations</span>
            <span className="text-sm text-gray-400">{stats?.locations_count || 0} items</span>
          </Button>
          <Button
            onClick={() => navigate(`/contacts?org=${id}`)}
            className="bg-gray-700 hover:bg-gray-600 text-white text-left h-auto py-4 px-4 flex flex-col"
          >
            <span className="font-semibold">Contacts</span>
            <span className="text-sm text-gray-400">{stats?.contacts_count || 0} items</span>
          </Button>
          <Button
            onClick={() => navigate(`/documentations?org=${id}`)}
            className="bg-gray-700 hover:bg-gray-600 text-white text-left h-auto py-4 px-4 flex flex-col"
          >
            <span className="font-semibold">Documentation</span>
            <span className="text-sm text-gray-400">{stats?.documentations_count || 0} items</span>
          </Button>
          <Button
            onClick={() => navigate(`/passwords?org=${id}`)}
            className="bg-gray-700 hover:bg-gray-600 text-white text-left h-auto py-4 px-4 flex flex-col"
          >
            <span className="font-semibold">Passwords</span>
            <span className="text-sm text-gray-400">{stats?.password_entries_count || 0} items</span>
          </Button>
          <Button
            onClick={() => navigate(`/configurations?org=${id}`)}
            className="bg-gray-700 hover:bg-gray-600 text-white text-left h-auto py-4 px-4 flex flex-col"
          >
            <span className="font-semibold">Configurations</span>
            <span className="text-sm text-gray-400">{stats?.configurations_count || 0} items</span>
          </Button>
        </div>
      </Card>

      {/* Metadata */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-foreground mb-4">Information</h2>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-400">
          <div>
            <span className="text-gray-500">Created:</span> {new Date(organization.created_at).toLocaleDateString()}
          </div>
          <div>
            <span className="text-gray-500">Last Updated:</span> {new Date(organization.updated_at).toLocaleDateString()}
          </div>
          {organization.created_by && (
            <div>
              <span className="text-gray-500">Created By:</span> {organization.created_by.email}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};
