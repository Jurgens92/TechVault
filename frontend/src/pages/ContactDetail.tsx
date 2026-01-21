import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { contactAPI } from '../services/core';
import { Contact } from '../types/core';
import { ArrowLeft, Edit, Trash2, Mail, Phone } from 'lucide-react';

export const ContactDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      contactAPI.getById(id).then(r => setContact(r.data)).finally(() => setLoading(false)).catch(() => {});
    }
  }, [id]);

  if (loading) return <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>;
  if (!contact) return <Card className="p-8 text-center"><p className="text-gray-400">Contact not found</p></Card>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div className="flex items-center gap-4">
          <Button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-700"><ArrowLeft className="w-5 h-5" /></Button>
          <h1 className="text-3xl font-bold text-foreground">{contact.full_name}</h1>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => navigate(`/contacts/${id}/edit`)} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"><Edit className="w-4 h-4" /> Edit</Button>
        </div>
      </div>

      <Card className="p-6 space-y-4">
        {contact.title && <div><span className="text-muted-foreground">Title:</span> <span className="text-foreground ml-2">{contact.title}</span></div>}
        <div><span className="text-muted-foreground">Organization:</span> <span className="text-foreground ml-2">{contact.organization_name}</span></div>
        <div className="flex gap-4">
          <a href={`mailto:${contact.email}`} className="flex items-center gap-2 text-blue-400 hover:text-blue-300"><Mail className="w-4 h-4" /> {contact.email}</a>
          {contact.phone && <a href={`tel:${contact.phone}`} className="flex items-center gap-2 text-blue-400 hover:text-blue-300"><Phone className="w-4 h-4" /> {contact.phone}</a>}
        </div>
      </Card>
    </div>
  );
};
