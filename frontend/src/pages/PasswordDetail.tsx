import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { passwordAPI } from '../services/core';
import { PasswordEntry } from '../types/core';
import { ArrowLeft, Edit, Eye, EyeOff } from 'lucide-react';

export const PasswordDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [pwd, setPwd] = useState<PasswordEntry | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [decryptedPassword, setDecryptedPassword] = useState<string | null>(null);
  const [passwordLoading, setPasswordLoading] = useState(false);

  useEffect(() => {
    if (id) {
      passwordAPI.getById(id).then(r => setPwd(r.data)).finally(() => setLoading(false)).catch(() => {});
    }
  }, [id]);

  const handleTogglePassword = async () => {
    if (showPassword) {
      // Hide password
      setShowPassword(false);
    } else {
      // Show password - fetch from secure endpoint if not already fetched
      if (!decryptedPassword && id) {
        setPasswordLoading(true);
        try {
          const response = await passwordAPI.retrievePassword(id);
          setDecryptedPassword(response.data.password);
          setShowPassword(true);
        } catch {
          // Handle error silently or show error message
        } finally {
          setPasswordLoading(false);
        }
      } else {
        setShowPassword(true);
      }
    }
  };

  if (loading) return <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>;
  if (!pwd) return <Card className="p-8 text-center"><p className="text-gray-400">Password not found</p></Card>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div className="flex items-center gap-4">
          <Button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-700"><ArrowLeft className="w-5 h-5" /></Button>
          <h1 className="text-3xl font-bold text-foreground">{pwd.name}</h1>
        </div>
        <Button onClick={() => navigate(`/passwords/${id}/edit`)} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"><Edit className="w-4 h-4" /> Edit</Button>
      </div>

      <Card className="p-6 space-y-4">
        <div>
          <span className="text-gray-400">Organization:</span>
          <span className="text-foreground ml-2">{pwd.organization_name}</span>
        </div>
        <div>
          <span className="text-gray-400">Category:</span>
          <span className="text-foreground ml-2">{pwd.category}</span>
        </div>
        {pwd.username && (
          <div>
            <span className="text-gray-400">Username:</span>
            <span className="text-foreground ml-2">{pwd.username}</span>
          </div>
        )}
        <div>
          <div className="text-gray-400 mb-2">Password</div>
          <div className="flex items-center gap-2">
            <code className="flex-1 px-4 py-2 bg-secondary rounded text-foreground">
              {passwordLoading ? 'Loading...' : (showPassword && decryptedPassword ? decryptedPassword : '••••••••')}
            </code>
            <Button onClick={handleTogglePassword} disabled={passwordLoading} className="p-2 hover:bg-gray-700">
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </Button>
          </div>
        </div>
        {pwd.url && (
          <div>
            <span className="text-gray-400">URL:</span>
            <a href={pwd.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 ml-2">{pwd.url}</a>
          </div>
        )}
      </Card>
    </div>
  );
};
