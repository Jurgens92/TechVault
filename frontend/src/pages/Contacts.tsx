import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { PageHeader } from '../components/PageHeader';
import { EmptyOrgState } from '../components/EmptyOrgState';
import { useOrganization } from '../contexts/OrganizationContext';
import { contactAPI } from '../services/core';
import { Contact } from '../types/core';
import { Users, Trash2, Edit, ChevronRight, Upload, Download, Plus } from 'lucide-react';

export const Contacts: React.FC = () => {
  const navigate = useNavigate();
  const { selectedOrg } = useOrganization();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<{
    created: number;
    errors: Array<{ row: number; error: string }>;
    message: string;
  } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (selectedOrg) {
      fetchContacts();
    } else {
      setContacts([]);
      setLoading(false);
    }
  }, [selectedOrg]);

  const fetchContacts = async () => {
    if (!selectedOrg) return;

    try {
      setLoading(true);
      const response = await contactAPI.byOrganization(selectedOrg.id.toString());
      const data: Contact[] = Array.isArray(response.data)
        ? response.data
        : ((response.data as any)?.results || []);
      setContacts(data);
      setError(null);
    } catch (err) {
      setError('Failed to load contacts');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Delete this contact?')) {
      try {
        await contactAPI.delete(id);
        setContacts(contacts.filter(c => c.id !== id));
      } catch (err) {
        setError('Failed to delete contact');
      }
    }
  };

  const handleDownloadExample = async () => {
    try {
      const response = await contactAPI.downloadExampleCSV();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'contacts_example.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download example CSV');
    }
  };

  const handleImportClick = () => {
    if (!selectedOrg) {
      setError('Please select an organization first');
      return;
    }
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !selectedOrg) return;

    try {
      setImporting(true);
      setError(null);
      setImportResult(null);

      const response = await contactAPI.importCSV(file, selectedOrg.id.toString());
      setImportResult(response.data);

      // Refresh the contacts list
      await fetchContacts();

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to import CSV');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Contacts"
        actionButton={{
          label: 'Add New',
          icon: Plus,
          onClick: () => navigate('/contacts/new'),
        }}
        search={{
          placeholder: 'Search contacts...',
          onSearch: () => {},
        }}
      />

      {!selectedOrg ? (
        <EmptyOrgState />
      ) : (
        <>
          {/* CSV Import/Export Section */}
          <Card className="p-4">
            <div className="flex items-center gap-4">
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
              />
              <Button
                onClick={handleImportClick}
                disabled={importing || !selectedOrg}
                className="bg-green-600 hover:bg-green-700 flex items-center gap-2"
              >
                <Upload className="w-4 h-4" />
                {importing ? 'Importing...' : 'Import CSV'}
              </Button>
              <Button
                onClick={handleDownloadExample}
                className="bg-blue-600 hover:bg-blue-700 flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download Example CSV
              </Button>
            </div>
          </Card>

          {/* Import Result */}
          {importResult && (
            <Card className={`p-4 ${importResult.errors.length > 0 ? 'bg-yellow-900/20 border-yellow-700' : 'bg-green-900/20 border-green-700'}`}>
              <h3 className="font-semibold mb-2">{importResult.message}</h3>
              {importResult.errors.length > 0 && (
                <div className="mt-2">
                  <p className="font-semibold text-sm mb-1">Errors:</p>
                  <ul className="list-disc list-inside text-sm space-y-1">
                    {importResult.errors.map((err, idx) => (
                      <li key={idx}>Row {err.row}: {err.error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </Card>
          )}

          {error && <div className="p-4 bg-red-900/20 border border-red-700 rounded-lg text-red-200">{error}</div>}

          {loading ? (
        <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>
      ) : contacts.length === 0 ? (
        <Card className="p-8 text-center">
          <Users className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-muted-foreground mb-4">No contacts found</p>
          <Button onClick={() => navigate('/contacts/new')} className="bg-blue-600 hover:bg-blue-700">Create First Contact</Button>
        </Card>
      ) : (
        <div className="grid gap-4">
          {contacts.map(contact => (
            <Card key={contact.id} className="p-6 hover:border-blue-500 cursor-pointer group" onClick={() => navigate(`/contacts/${contact.id}`)}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-foreground group-hover:text-primary">{contact.full_name}</h3>
                  {contact.title && <p className="text-muted-foreground text-sm">{contact.title}</p>}
                  {contact.location_name && <p className="text-muted-foreground text-sm">📍 {contact.location_name}</p>}
                  <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                    <a href={`mailto:${contact.email}`} className="hover:text-blue-400">{contact.email}</a>
                    {contact.phone && <span>{contact.phone}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button onClick={(e) => { e.stopPropagation(); navigate(`/contacts/${contact.id}/edit`); }} className="p-2 hover:bg-gray-700"><Edit className="w-4 h-4" /></Button>
                  <Button onClick={(e) => { e.stopPropagation(); handleDelete(contact.id); }} className="p-2 hover:bg-red-900/20 text-red-400"><Trash2 className="w-4 h-4" /></Button>
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
