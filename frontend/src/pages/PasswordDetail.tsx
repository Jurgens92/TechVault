import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { passwordAPI } from '../services/core';
import { PasswordEntry } from '../types/core';
import { ArrowLeft, Check, Copy, Edit, Eye, EyeOff } from 'lucide-react';
import { notify } from '@/components/Feedback';
import { getErrorMessage } from '@/utils/errors';

// A revealed password is hidden again (and dropped from memory) after this long
const AUTO_HIDE_SECONDS = 30;
// The clipboard is cleared after this long, if it still holds the password
const CLIPBOARD_CLEAR_SECONDS = 30;

export const PasswordDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [pwd, setPwd] = useState<PasswordEntry | null>(null);
  const [loading, setLoading] = useState(true);
  const [revealed, setRevealed] = useState<string | null>(null);
  const [secondsLeft, setSecondsLeft] = useState(0);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [copied, setCopied] = useState<'password' | 'username' | null>(null);
  const clipboardTimer = useRef<number | null>(null);

  useEffect(() => {
    if (id) {
      passwordAPI.getById(id)
        .then(r => setPwd(r.data))
        .catch((err) => notify.error(getErrorMessage(err, 'Could not load this password entry.')))
        .finally(() => setLoading(false));
    }
  }, [id]);

  const hide = useCallback(() => {
    setRevealed(null);
    setSecondsLeft(0);
  }, []);

  // Countdown that hides the password again
  useEffect(() => {
    if (revealed === null) return;
    if (secondsLeft <= 0) {
      hide();
      return;
    }
    const timer = window.setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => window.clearTimeout(timer);
  }, [revealed, secondsLeft, hide]);

  useEffect(() => () => {
    if (clipboardTimer.current) window.clearTimeout(clipboardTimer.current);
  }, []);

  // Every reveal/copy goes to the server, so each access is recorded in the audit log
  const fetchPassword = async (): Promise<string | null> => {
    if (!id) return null;
    setPasswordLoading(true);
    setPasswordError(null);
    try {
      const response = await passwordAPI.retrievePassword(id);
      return response.data.password;
    } catch (err) {
      setPasswordError(getErrorMessage(err, 'Failed to retrieve password. Please try again.'));
      return null;
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleTogglePassword = async () => {
    if (revealed !== null) {
      hide();
      return;
    }
    const value = await fetchPassword();
    if (value !== null) {
      setRevealed(value);
      setSecondsLeft(AUTO_HIDE_SECONDS);
    }
  };

  const flashCopied = (what: 'password' | 'username') => {
    setCopied(what);
    window.setTimeout(() => setCopied((current) => (current === what ? null : current)), 2000);
  };

  const handleCopyPassword = async () => {
    const value = revealed ?? await fetchPassword();
    if (value === null) return;
    try {
      await navigator.clipboard.writeText(value);
      flashCopied('password');
      notify.success(`Password copied. The clipboard will be cleared in ${CLIPBOARD_CLEAR_SECONDS} seconds.`);
      if (clipboardTimer.current) window.clearTimeout(clipboardTimer.current);
      clipboardTimer.current = window.setTimeout(async () => {
        try {
          // Only clear if the clipboard still holds this password
          if ((await navigator.clipboard.readText()) === value) {
            await navigator.clipboard.writeText('');
          }
        } catch {
          // Reading the clipboard needs permission/focus; if unavailable, clear anyway
          navigator.clipboard.writeText('').catch(() => undefined);
        }
      }, CLIPBOARD_CLEAR_SECONDS * 1000);
    } catch {
      notify.error('Could not copy to the clipboard. Reveal the password and copy it manually.');
    }
  };

  const handleCopyUsername = async () => {
    if (!pwd?.username) return;
    try {
      await navigator.clipboard.writeText(pwd.username);
      flashCopied('username');
    } catch {
      notify.error('Could not copy to the clipboard.');
    }
  };

  if (loading) return <div className="text-center py-12"><div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>;
  if (!pwd) return <Card className="p-8 text-center"><p className="text-gray-400">Password not found</p></Card>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div className="flex items-center gap-4">
          <Button onClick={() => navigate(-1)} className="p-2 hover:bg-gray-700" aria-label="Back"><ArrowLeft className="w-5 h-5" /></Button>
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
          <div className="flex items-center gap-2">
            <span className="text-gray-400">Username:</span>
            <span className="text-foreground">{pwd.username}</span>
            <Button onClick={handleCopyUsername} className="p-1.5 hover:bg-gray-700" aria-label="Copy username" title="Copy username">
              {copied === 'username' ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
            </Button>
          </div>
        )}
        <div>
          <div className="text-gray-400 mb-2">Password</div>
          <div className="flex items-center gap-2">
            <code className="flex-1 px-4 py-2 bg-secondary rounded text-foreground break-all">
              {passwordLoading ? 'Loading...' : (revealed !== null ? revealed : '••••••••')}
            </code>
            <Button
              onClick={handleTogglePassword}
              disabled={passwordLoading}
              className="p-2 hover:bg-gray-700"
              aria-label={revealed !== null ? 'Hide password' : 'Show password'}
              title={revealed !== null ? 'Hide password' : 'Show password'}
            >
              {revealed !== null ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </Button>
            <Button
              onClick={handleCopyPassword}
              disabled={passwordLoading}
              className="p-2 hover:bg-gray-700"
              aria-label="Copy password"
              title="Copy password"
            >
              {copied === 'password' ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
            </Button>
          </div>
          {revealed !== null && (
            <p className="text-gray-400 text-sm mt-1">Hides automatically in {secondsLeft}s. Each view is recorded in the audit log.</p>
          )}
          {passwordError && <p className="text-red-400 text-sm mt-1">{passwordError}</p>}
        </div>
        {pwd.url && (
          <div>
            <span className="text-gray-400">URL:</span>
            <a href={pwd.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 ml-2 break-all">{pwd.url}</a>
          </div>
        )}
        {pwd.notes && (
          <div>
            <div className="text-gray-400 mb-2">Notes</div>
            <p className="text-foreground whitespace-pre-wrap break-words">{pwd.notes}</p>
          </div>
        )}
      </Card>
    </div>
  );
};
