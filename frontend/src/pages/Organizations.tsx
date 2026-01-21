import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { PageHeader } from '../components/PageHeader';
import { organizationAPI } from '../services/core';
import { Organization } from '../types/core';
import { Building2, MapPin, ChevronRight, Trash2, Edit, Plus } from 'lucide-react';

export const Organizations: React.FC = () => {
  const navigate = useNavigate();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      const response = await organizationAPI.getAll();
      setOrganizations(response.data.results);
      setError(null);
    } catch (err) {
      setError('Failed to load organizations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    if (query.trim()) {
      try {
        const response = await organizationAPI.search(query);
        setOrganizations(response.data);
      } catch (err) {
        console.error('Search failed:', err);
      }
    } else {
      fetchOrganizations();
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this organization?')) {
      try {
        await organizationAPI.delete(id);
        setOrganizations(organizations.filter(org => org.id !== id));
      } catch (err) {
        setError('Failed to delete organization');
        console.error(err);
      }
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Organizations"
        actionButton={{
          label: 'Add New',
          icon: Plus,
          onClick: () => navigate('/organizations/new'),
        }}
        search={{
          placeholder: 'Search organizations...',
          onSearch: handleSearch,
        }}
      />

      {error && (
        <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-muted-foreground">Loading organizations...</p>
        </div>
      ) : organizations.length === 0 ? (
        <Card className="p-8 text-center">
          <Building2 className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-muted-foreground mb-4">No organizations found</p>
          <Button
            onClick={() => navigate('/organizations/new')}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Create First Organization
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4">
          {organizations.map(org => (
            <Card
              key={org.id}
              className="p-6 hover:border-blue-500 transition-colors cursor-pointer group"
              onClick={() => navigate(`/organizations/${org.id}`)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <Building2 className="w-5 h-5 text-blue-500" />
                    <h3 className="text-lg font-semibold text-foreground group-hover:text-primary">
                      {org.name}
                    </h3>
                    {!org.is_active && (
                      <span className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded">
                        Inactive
                      </span>
                    )}
                  </div>
                  {org.description && (
                    <p className="text-muted-foreground text-sm mb-3">{org.description}</p>
                  )}
                  <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                    {org.email && (
                      <div>
                        <span className="text-gray-500">Email:</span> {org.email}
                      </div>
                    )}
                    {org.city && (
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {org.city}
                        {org.country && `, ${org.country}`}
                      </div>
                    )}
                    {org.phone && (
                      <div>
                        <span className="text-gray-500">Phone:</span> {org.phone}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/organizations/${org.id}/edit`);
                    }}
                    className="p-2 hover:bg-gray-700 text-gray-300"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(org.id);
                    }}
                    className="p-2 hover:bg-red-900/20 text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                  <ChevronRight className="w-5 h-5 text-gray-500 group-hover:text-blue-400" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
