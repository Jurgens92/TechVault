import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { locationAPI } from '../services/core';
import { Location } from '../types/core';
import { ArrowLeft, Edit, Trash2, MapPin, Phone } from 'lucide-react';

export const LocationDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [location, setLocation] = useState<Location | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) fetchLocation();
  }, [id]);

  const fetchLocation = async () => {
    try {
      if (!id) return;
      const response = await locationAPI.getById(id);
      setLocation(response.data);
    } catch (err) {
      setError('Failed to load location');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Delete this location?')) {
      try {
        if (!id) return;
        await locationAPI.delete(id);
        navigate('/locations');
      } catch (err) {
        setError('Failed to delete location');
      }
    }
  };

  if (loading) return <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>;

  if (!location) return <Card className="p-8 text-center"><p className="text-gray-400">Location not found</p></Card>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div className="flex items-center gap-4">
          <Button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-700"><ArrowLeft className="w-5 h-5" /></Button>
          <h1 className="text-3xl font-bold text-foreground">{location.name}</h1>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => navigate(`/locations/${id}/edit`)} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"><Edit className="w-4 h-4" /> Edit</Button>
          <Button onClick={handleDelete} className="p-2 hover:bg-red-900/20 text-red-400"><Trash2 className="w-5 h-5" /></Button>
        </div>
      </div>

      {error && <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">{error}</div>}

      <Card className="p-6 space-y-4">
        <h2 className="text-xl font-semibold text-foreground mb-4">Details</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-muted-foreground">Organization</div>
            <p className="text-foreground">{location.organization_name}</p>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Address</div>
            <p className="text-foreground">{location.address}</p>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">City</div>
            <p className="text-foreground">{location.city}, {location.state_province}</p>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Country</div>
            <p className="text-foreground">{location.country}</p>
          </div>
          {location.phone && (
            <div>
              <div className="text-sm text-muted-foreground">Phone</div>
              <p className="text-foreground">{location.phone}</p>
            </div>
          )}
          <div>
            <div className="text-sm text-muted-foreground">Status</div>
            <p className="text-foreground">{location.is_active ? 'Active' : 'Inactive'}</p>
          </div>
        </div>
      </Card>

      {location.description && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Description</h2>
          <p className="text-gray-300">{location.description}</p>
        </Card>
      )}
    </div>
  );
};
