import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { configurationAPI } from '../services/core';
import { Configuration } from '../types/core';
import { ArrowLeft, Edit } from 'lucide-react';

export const ConfigurationDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [config, setConfig] = useState<Configuration | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      configurationAPI.getById(id).then(r => setConfig(r.data)).finally(() => setLoading(false)).catch(() => {});
    }
  }, [id]);

  if (loading) return <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>;
  if (!config) return <Card className="p-8 text-center"><p className="text-gray-400">Configuration not found</p></Card>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div className="flex items-center gap-4">
          <Button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-700"><ArrowLeft className="w-5 h-5" /></Button>
          <h1 className="text-3xl font-bold text-foreground">{config.name}</h1>
        </div>
        <Button onClick={() => navigate(`/configurations/${id}/edit`)} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"><Edit className="w-4 h-4" /> Edit</Button>
      </div>

      <Card className="p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-muted-foreground">Organization:</span>
            <span className="text-foreground ml-2">{config.organization_name}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Type:</span>
            <span className="text-foreground ml-2">{config.config_type}</span>
          </div>
          {config.version && (
            <div>
              <span className="text-muted-foreground">Version:</span>
              <span className="text-foreground ml-2">{config.version}</span>
            </div>
          )}
          <div>
            <span className="text-muted-foreground">Status:</span>
            <span className="text-foreground ml-2">{config.is_active ? 'Active' : 'Inactive'}</span>
          </div>
        </div>
      </Card>

      {config.description && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold text-foreground mb-3">Description</h2>
          <p className="text-gray-300">{config.description}</p>
        </Card>
      )}

      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-3">Configuration Content</h2>
        <pre className="bg-gray-900 p-4 rounded overflow-x-auto text-gray-300 text-sm"><code>{config.content}</code></pre>
      </Card>
    </div>
  );
};
