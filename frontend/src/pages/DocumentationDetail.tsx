import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { documentationAPI } from '../services/core';
import { Documentation } from '../types/core';
import { ArrowLeft, Edit } from 'lucide-react';

export const DocumentationDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [doc, setDoc] = useState<Documentation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      documentationAPI.getById(id).then(r => setDoc(r.data)).finally(() => setLoading(false)).catch(() => {});
    }
  }, [id]);

  if (loading) return <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>;
  if (!doc) return <Card className="p-8 text-center"><p className="text-muted-foreground">Documentation not found</p></Card>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div className="flex items-center gap-4">
          <Button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-700"><ArrowLeft className="w-5 h-5" /></Button>
          <h1 className="text-3xl font-bold text-foreground">{doc.title}</h1>
          {doc.is_published && <span className="text-xs bg-green-900/30 text-green-300 px-3 py-1 rounded">Published</span>}
        </div>
        <Button onClick={() => navigate(`/documentations/${id}/edit`)} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"><Edit className="w-4 h-4" /> Edit</Button>
      </div>

      <Card className="p-6">
        <div className="flex gap-4 mb-6 text-sm text-muted-foreground">
          <span>{doc.category}</span>
          <span>v{doc.version}</span>
          <span>{new Date(doc.created_at).toLocaleDateString()}</span>
        </div>
        <div className="prose dark:prose-invert max-w-none text-foreground whitespace-pre-wrap">{doc.content}</div>
      </Card>
    </div>
  );
};
