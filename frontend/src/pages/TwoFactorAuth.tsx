import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Shield, QrCode, Key, AlertCircle, CheckCircle, Copy } from 'lucide-react';
import api from '@/services/api';

interface TwoFAStatus {
  twofa_enabled: boolean;
  backup_codes_remaining: number;
  email: string;
}

const TwoFactorAuth: React.FC = () => {
  const { user } = useAuth();
  const [status, setStatus] = useState<TwoFAStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Setup state
  const [showSetup, setShowSetup] = useState(false);
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [verifyToken, setVerifyToken] = useState('');

  // Backup codes state
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  // Disable state
  const [showDisable, setShowDisable] = useState(false);
  const [disablePassword, setDisablePassword] = useState('');

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const response = await api.get('/api/auth/2fa/status/');
      setStatus(response.data);
    } catch (err: any) {
      console.error('Failed to load 2FA status:', err);
    }
  };

  const handleSetup = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.post('/api/auth/2fa/setup/');
      setQrCode(response.data.qr_code);
      setSecret(response.data.secret);
      setShowSetup(true);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to setup 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleEnable = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');
      const response = await api.post('/api/auth/2fa/enable/', { token: verifyToken });
      setBackupCodes(response.data.backup_codes);
      setShowBackupCodes(true);
      setShowSetup(false);
      setSuccess('2FA enabled successfully!');
      await loadStatus();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to enable 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleDisable = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');
      await api.post('/api/auth/2fa/disable/', { password: disablePassword });
      setShowDisable(false);
      setDisablePassword('');
      setSuccess('2FA disabled successfully');
      await loadStatus();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to disable 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateBackupCodes = async () => {
    const password = prompt('Enter your password to regenerate backup codes:');
    if (!password) return;

    try {
      setLoading(true);
      setError('');
      const response = await api.post('/api/auth/2fa/backup-codes/regenerate/', { password });
      setBackupCodes(response.data.backup_codes);
      setShowBackupCodes(true);
      setSuccess('Backup codes regenerated successfully!');
      await loadStatus();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to regenerate backup codes');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard!');
    setTimeout(() => setSuccess(''), 2000);
  };

  const copyAllBackupCodes = () => {
    const allCodes = backupCodes.join('\n');
    copyToClipboard(allCodes);
  };

  if (!status) {
    return (
      <div className="container mx-auto p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-6">
            <Shield className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold">Two-Factor Authentication</h1>
          </div>
          <Card>
            <CardContent className="p-6">
              <p>Loading...</p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Shield className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Two-Factor Authentication</h1>
        </div>

        {/* Alerts */}
        {error && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md border border-destructive/20 mb-4 flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-500/10 text-green-600 text-sm p-3 rounded-md border border-green-500/20 mb-4 flex items-center gap-2">
            <CheckCircle className="h-4 w-4" />
            {success}
          </div>
        )}

        {/* Backup Codes Display */}
        {showBackupCodes && backupCodes.length > 0 && (
          <Card className="mb-6 border-yellow-500/50 bg-yellow-500/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                Backup Codes
              </CardTitle>
              <CardDescription>
                Save these codes in a secure location. You can use them to access your account if you lose your authenticator device.
                Each code can only be used once.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-muted p-4 rounded-lg mb-4">
                <div className="grid grid-cols-2 gap-2 font-mono text-sm">
                  {backupCodes.map((code, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-background rounded border">
                      <span>{code}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(code)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex gap-2">
                <Button onClick={copyAllBackupCodes} variant="outline">
                  <Copy className="h-4 w-4 mr-2" />
                  Copy All
                </Button>
                <Button onClick={() => setShowBackupCodes(false)}>
                  I've Saved My Codes
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Current Status */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Current Status</CardTitle>
            <CardDescription>
              Two-factor authentication adds an extra layer of security to your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${status.twofa_enabled ? 'bg-green-500/10' : 'bg-muted'}`}>
                  <Shield className={`h-6 w-6 ${status.twofa_enabled ? 'text-green-600' : 'text-muted-foreground'}`} />
                </div>
                <div>
                  <p className="font-medium">
                    {status.twofa_enabled ? '2FA Enabled' : '2FA Disabled'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {status.twofa_enabled
                      ? `${status.backup_codes_remaining} backup codes remaining`
                      : 'Protect your account with two-factor authentication'}
                  </p>
                </div>
              </div>
              {!status.twofa_enabled ? (
                <Button onClick={handleSetup} disabled={loading}>
                  Enable 2FA
                </Button>
              ) : (
                <Button variant="destructive" onClick={() => setShowDisable(true)} disabled={loading}>
                  Disable 2FA
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Setup Flow */}
        {showSetup && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <QrCode className="h-5 w-5" />
                Setup Two-Factor Authentication
              </CardTitle>
              <CardDescription>
                Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-center p-4 bg-white rounded-lg">
                  <img src={qrCode} alt="QR Code" className="w-64 h-64" />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Or enter this code manually:</label>
                  <div className="flex gap-2">
                    <Input value={secret} readOnly className="font-mono" />
                    <Button variant="outline" onClick={() => copyToClipboard(secret)}>
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <form onSubmit={handleEnable} className="space-y-4">
                  <div className="space-y-2">
                    <label htmlFor="verify-token" className="text-sm font-medium">
                      Verify Code
                    </label>
                    <Input
                      id="verify-token"
                      type="text"
                      placeholder="Enter 6-digit code"
                      value={verifyToken}
                      onChange={(e) => setVerifyToken(e.target.value)}
                      required
                      maxLength={6}
                      disabled={loading}
                    />
                    <p className="text-xs text-muted-foreground">
                      Enter the 6-digit code from your authenticator app to verify
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <Button type="submit" disabled={loading || verifyToken.length !== 6}>
                      {loading ? 'Verifying...' : 'Enable 2FA'}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowSetup(false);
                        setVerifyToken('');
                        setQrCode('');
                        setSecret('');
                      }}
                      disabled={loading}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Disable Form */}
        {showDisable && (
          <Card>
            <CardHeader>
              <CardTitle>Disable Two-Factor Authentication</CardTitle>
              <CardDescription>
                Enter your password to disable 2FA. This will make your account less secure.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleDisable} className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="disable-password" className="text-sm font-medium">
                    Password
                  </label>
                  <Input
                    id="disable-password"
                    type="password"
                    placeholder="Enter your password"
                    value={disablePassword}
                    onChange={(e) => setDisablePassword(e.target.value)}
                    required
                    disabled={loading}
                  />
                </div>

                <div className="flex gap-2">
                  <Button type="submit" variant="destructive" disabled={loading}>
                    {loading ? 'Disabling...' : 'Disable 2FA'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowDisable(false);
                      setDisablePassword('');
                    }}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Backup Codes Management */}
        {status.twofa_enabled && !showSetup && !showDisable && (
          <Card>
            <CardHeader>
              <CardTitle>Backup Codes</CardTitle>
              <CardDescription>
                Backup codes can be used to access your account if you lose your authenticator device
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{status.backup_codes_remaining} codes remaining</p>
                  <p className="text-sm text-muted-foreground">
                    {status.backup_codes_remaining < 3 && 'Consider regenerating your backup codes'}
                  </p>
                </div>
                <Button onClick={handleRegenerateBackupCodes} variant="outline" disabled={loading}>
                  Regenerate Codes
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default TwoFactorAuth;
