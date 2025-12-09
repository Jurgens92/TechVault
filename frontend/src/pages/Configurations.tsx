import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { PageHeader } from '../components/PageHeader';
import { EmptyOrgState } from '../components/EmptyOrgState';
import { useOrganization } from '../contexts/OrganizationContext';
import { configurationAPI } from '../services/core';
import { Configuration } from '../types/core';
import { Settings, Trash2, Edit, ChevronRight, Plus } from 'lucide-react';

export const Configurations: React.FC = () => {
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [configs, setConfigs] = useState<Configuration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedOrg) {
      fetchConfigs();
    } else {
      setConfigs([]);
      setLoading(false);
    }
  }, [selectedOrg]);

  const fetchConfigs = async () => {
    if (!selectedOrg) return;

    try {
      setLoading(true);
      const response = await configurationAPI.byOrganization(selectedOrg.id.toString());
      const data: Configuration[] = Array.isArray(response.data)
        ? response.data
        : ((response.data as any)?.results || []);
      setConfigs(data);
      setError(null);
    } catch (err) {
      setError('Failed to load configurations');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Delete this configuration?')) {
      try {
        await configurationAPI.delete(id);
        setConfigs(configs.filter(c => c.id !== id));
      } catch (err) {
        setError('Failed to delete');
      }
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Configurations"
        actionButton={{
          label: 'Add New',
          icon: Plus,
          onClick: () => navigate('/configurations/new'),
        }}
        search={{
          placeholder: 'Search configurations...',
          onSearch: () => {},
        }}
      />

      {!selectedOrg ? (
        <EmptyOrgState />
      ) : (
        <>
          {error && <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">{error}</div>}
          {loading ? (
        <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>
      ) : configs.length === 0 ? (
        <Card className="p-8 text-center">
          <Settings className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <Button onClick={() => navigate('/configurations/new')} className="mt-4 bg-blue-600 hover:bg-blue-700">Create Configuration</Button>
        </Card>
      ) : (
        <div className="grid gap-4">
          {configs.map(config => (
            <Card key={config.id} className="p-6 hover:border-blue-500 cursor-pointer group" onClick={() => navigate(`/configurations/${config.id}`)}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-white group-hover:text-blue-400">{config.name}</h3>
                  <p className="text-gray-400 text-sm">{config.config_type} • {config.organization_name}</p>
                  {config.description && <p className="text-gray-500 text-sm mt-1 line-clamp-1">{config.description}</p>}
                </div>
                <div className="flex items-center gap-2">
                  <Button onClick={(e) => { e.stopPropagation(); navigate(`/configurations/${config.id}/edit`); }} className="p-2 hover:bg-gray-700"><Edit className="w-4 h-4" /></Button>
                  <Button onClick={(e) => { e.stopPropagation(); handleDelete(config.id); }} className="p-2 hover:bg-red-900/20 text-red-400"><Trash2 className="w-4 h-4" /></Button>
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
