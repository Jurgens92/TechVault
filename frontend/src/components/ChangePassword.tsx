import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { KeyRound, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { authService } from '@/services/auth';
import { notify } from '@/components/Feedback';
import { getErrorMessage } from '@/utils/errors';

/** Lets the signed-in user change their own password (current password required). */
const ChangePassword: React.FC = () => {
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (next !== confirm) {
      setError('The new passwords do not match.');
      return;
    }
    try {
      setSaving(true);
      await authService.changePassword(current, next);
      setCurrent('');
      setNext('');
      setConfirm('');
      notify.success('Your password has been changed.');
    } catch (err) {
      setError(getErrorMessage(err, 'Could not change your password.'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
        <h3 className="flex items-center gap-2 text-sm font-medium">
          <KeyRound className="h-4 w-4" />
          Change password
        </h3>
        {error && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md border border-destructive/20 whitespace-pre-line">
            {error}
          </div>
        )}
        <div className="space-y-2">
          <label htmlFor="current_password" className="text-sm font-medium">Current password</label>
          <Input
            id="current_password"
            type="password"
            autoComplete="current-password"
            value={current}
            onChange={(e) => setCurrent(e.target.value)}
            required
            disabled={saving}
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="new_password" className="text-sm font-medium">New password</label>
          <Input
            id="new_password"
            type="password"
            autoComplete="new-password"
            value={next}
            onChange={(e) => setNext(e.target.value)}
            required
            minLength={8}
            disabled={saving}
          />
        </div>
        <div className="space-y-2">
          <label htmlFor="confirm_password" className="text-sm font-medium">Confirm new password</label>
          <Input
            id="confirm_password"
            type="password"
            autoComplete="new-password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
            minLength={8}
            disabled={saving}
          />
        </div>
        <Button type="submit" disabled={saving || !current || !next || !confirm}>
          {saving ? 'Saving...' : 'Change password'}
        </Button>
      </form>

      <div className="pt-4 border-t border-border">
        <Link to="/2fa" className="inline-flex items-center gap-2 text-sm text-primary hover:underline">
          <ShieldCheck className="h-4 w-4" />
          Manage two-factor authentication and backup codes
        </Link>
      </div>
    </div>
  );
};

export default ChangePassword;
