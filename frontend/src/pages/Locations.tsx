import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { PageHeader } from '../components/PageHeader';
import { EmptyOrgState } from '../components/EmptyOrgState';
import { useOrganization } from '../contexts/OrganizationContext';
import { locationAPI } from '../services/core';
import { Location } from '../types/core';
import { MapPin, Trash2, Edit, ChevronRight, Plus } from 'lucide-react';

export const Locations: React.FC = () => {
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    if (selectedOrg) {
      fetchLocations();
    } else {
      setLocations([]);
      setLoading(false);
    }
  }, [selectedOrg]);

  const fetchLocations = async () => {
    if (!selectedOrg) return;

    try {
      setLoading(true);
      const response = await locationAPI.byOrganization(selectedOrg.id.toString());
      const data: Location[] = Array.isArray(response.data)
        ? response.data
        : ((response.data as any)?.results || []);
      setLocations(data);
      setError(null);
    } catch (err) {
      setError('Failed to load locations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const getFilteredLocations = (): Location[] => {
    if (!searchQuery.trim()) {
      return locations;
    }
    const query = searchQuery.toLowerCase();
    return locations.filter(loc =>
      loc.name?.toLowerCase().includes(query) ||
      loc.address?.toLowerCase().includes(query) ||
      loc.city?.toLowerCase().includes(query) ||
      loc.country?.toLowerCase().includes(query) ||
      loc.organization_name?.toLowerCase().includes(query)
    );
  };

  const filteredLocations = getFilteredLocations();

  const handleDelete = async (id: string) => {
    if (window.confirm('Delete this location?')) {
      try {
        await locationAPI.delete(id);
        setLocations(locations.filter(loc => loc.id !== id));
      } catch (err) {
        setError('Failed to delete location');
      }
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Locations"
        actionButton={{
          label: 'Add New',
          icon: Plus,
          onClick: () => navigate('/locations/new'),
        }}
        search={{
          placeholder: 'Search locations...',
          onSearch: handleSearch,
        }}
      />

      {!selectedOrg ? (
        <EmptyOrgState />
      ) : (
        <>
          {error && (
            <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">{error}</div>
          )}

          {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-muted-foreground">Loading locations...</p>
        </div>
      ) : filteredLocations.length === 0 ? (
        <Card className="p-8 text-center">
          <MapPin className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-muted-foreground mb-4">{searchQuery ? 'No locations match your search' : 'No locations found'}</p>
          {!searchQuery && <Button onClick={() => navigate('/locations/new')} className="bg-blue-600 hover:bg-blue-700">
            Create First Location
          </Button>}
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredLocations.map(loc => (
            <Card
              key={loc.id}
              className="p-6 hover:border-blue-500 transition-colors cursor-pointer group"
              onClick={() => navigate(`/locations/${loc.id}`)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <MapPin className="w-5 h-5 text-green-500" />
                    <h3 className="text-lg font-semibold text-foreground group-hover:text-primary">
                      {loc.name}
                    </h3>
                  </div>
                  <p className="text-muted-foreground text-sm mb-2">{loc.organization_name}</p>
                  <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
                    <div>{loc.address}</div>
                    <div>{loc.city}, {loc.country}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/locations/${loc.id}/edit`);
                    }}
                    className="p-2 hover:bg-gray-700 text-gray-300"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(loc.id);
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
        </>
      )}
    </div>
  );
};
