import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { PageHeader } from '../components/PageHeader';
import { EmptyOrgState } from '../components/EmptyOrgState';
import { useOrganization } from '../contexts/OrganizationContext';
import { documentationAPI } from '../services/core';
import { Documentation } from '../types/core';
import { FileText, Trash2, Edit, ChevronRight, Plus } from 'lucide-react';

export const Documentations: React.FC = () => {
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [docs, setDocs] = useState<Documentation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    if (selectedOrg) {
      fetchDocs();
    } else {
      setDocs([]);
      setLoading(false);
    }
  }, [selectedOrg]);

  const fetchDocs = async () => {
    if (!selectedOrg) return;

    try {
      setLoading(true);
      const response = await documentationAPI.byOrganization(selectedOrg.id.toString());
      const data: Documentation[] = Array.isArray(response.data)
        ? response.data
        : ((response.data as any)?.results || []);
      setDocs(data);
      setError(null);
    } catch (err) {
      setError('Failed to load documentations');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const getFilteredDocs = (): Documentation[] => {
    if (!searchQuery.trim()) {
      return docs;
    }
    const query = searchQuery.toLowerCase();
    return docs.filter(doc =>
      doc.title?.toLowerCase().includes(query) ||
      doc.content?.toLowerCase().includes(query) ||
      doc.category?.toLowerCase().includes(query) ||
      doc.tags?.toLowerCase().includes(query) ||
      doc.organization_name?.toLowerCase().includes(query)
    );
  };

  const filteredDocs = getFilteredDocs();

  const handleDelete = async (id: string) => {
    if (window.confirm('Delete this documentation?')) {
      try {
        await documentationAPI.delete(id);
        setDocs(docs.filter(d => d.id !== id));
      } catch (err) {
        setError('Failed to delete');
      }
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Documentation"
        actionButton={{
          label: 'Add New',
          icon: Plus,
          onClick: () => navigate('/documentations/new'),
        }}
        search={{
          placeholder: 'Search documentations...',
          onSearch: handleSearch,
        }}
      />

      {!selectedOrg ? (
        <EmptyOrgState />
      ) : (
        <>
          {error && <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">{error}</div>}
          {loading ? (
        <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>
      ) : filteredDocs.length === 0 ? (
        <Card className="p-8 text-center">
          <FileText className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-muted-foreground mb-4">{searchQuery ? 'No documentation matches your search' : 'No documentation found'}</p>
          {!searchQuery && <Button onClick={() => navigate('/documentations/new')} className="mt-4 bg-blue-600 hover:bg-blue-700">Create Documentation</Button>}
        </Card>
      ) : (
        <div className="grid gap-4">
          {filteredDocs.map(doc => (
            <Card key={doc.id} className="p-6 hover:border-blue-500 cursor-pointer group" onClick={() => navigate(`/documentations/${doc.id}`)}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-foreground group-hover:text-primary">{doc.title}</h3>
                  <p className="text-muted-foreground text-sm mt-1">{doc.category} • {doc.organization_name}</p>
                  <p className="text-gray-500 text-sm mt-2 line-clamp-2">{doc.content}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Button onClick={(e) => { e.stopPropagation(); navigate(`/documentations/${doc.id}/edit`); }} className="p-2 hover:bg-gray-700"><Edit className="w-4 h-4" /></Button>
                  <Button onClick={(e) => { e.stopPropagation(); handleDelete(doc.id); }} className="p-2 hover:bg-red-900/20 text-red-400"><Trash2 className="w-4 h-4" /></Button>
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
