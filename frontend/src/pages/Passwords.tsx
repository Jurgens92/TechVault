import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { PageHeader } from '../components/PageHeader';
import { EmptyOrgState } from '../components/EmptyOrgState';
import { useOrganization } from '../contexts/OrganizationContext';
import { passwordAPI } from '../services/core';
import { PasswordEntry } from '../types/core';
import { Lock, Trash2, Edit, ChevronRight, Plus } from 'lucide-react';

export const Passwords: React.FC = () => {
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [passwords, setPasswords] = useState<PasswordEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedOrg) {
      fetchPasswords();
    } else {
      setPasswords([]);
      setLoading(false);
    }
  }, [selectedOrg]);

  const fetchPasswords = async () => {
    if (!selectedOrg) return;

    try {
      setLoading(true);
      const response = await passwordAPI.byOrganization(selectedOrg.id.toString());
      const data: PasswordEntry[] = Array.isArray(response.data)
        ? response.data
        : ((response.data as any)?.results || []);
      setPasswords(data);
      setError(null);
    } catch (err) {
      setError('Failed to load passwords');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Delete this password entry?')) {
      try {
        await passwordAPI.delete(id);
        setPasswords(passwords.filter(p => p.id !== id));
      } catch (err) {
        setError('Failed to delete');
      }
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Password Vault"
        actionButton={{
          label: 'Add New',
          icon: Plus,
          onClick: () => navigate('/passwords/new'),
        }}
        search={{
          placeholder: 'Search passwords...',
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
      ) : passwords.length === 0 ? (
        <Card className="p-8 text-center">
          <Lock className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <Button onClick={() => navigate('/passwords/new')} className="mt-4 bg-blue-600 hover:bg-blue-700">Add Password</Button>
        </Card>
      ) : (
        <div className="grid gap-4">
          {passwords.map(pwd => (
            <Card key={pwd.id} className="p-6 hover:border-blue-500 cursor-pointer group" onClick={() => navigate(`/passwords/${pwd.id}`)}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Lock className="w-4 h-4 text-yellow-500" />
                    <h3 className="text-lg font-semibold text-foreground group-hover:text-primary">{pwd.name}</h3>
                  </div>
                  <p className="text-gray-400 text-sm">{pwd.category} • {pwd.organization_name}</p>
                  {pwd.username && <p className="text-gray-500 text-sm mt-1">{pwd.username}</p>}
                </div>
                <div className="flex items-center gap-2">
                  <Button onClick={(e) => { e.stopPropagation(); navigate(`/passwords/${pwd.id}/edit`); }} className="p-2 hover:bg-gray-700"><Edit className="w-4 h-4" /></Button>
                  <Button onClick={(e) => { e.stopPropagation(); handleDelete(pwd.id); }} className="p-2 hover:bg-red-900/20 text-red-400"><Trash2 className="w-4 h-4" /></Button>
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
