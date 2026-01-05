import React, { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Shield, QrCode, Key, AlertCircle, CheckCircle, Copy, ArrowRight, Smartphone } from 'lucide-react';
import api from '@/services/api';

type SetupStep = 'welcome' | 'scan' | 'verify' | 'backup' | 'complete';

const TwoFactorSetup: React.FC = () => {
  const navigate = useNavigate();
  const { refreshUser, user, isAuthenticated, loading } = useAuth();

  const [step, setStep] = useState<SetupStep>('welcome');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Setup data
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [verifyToken, setVerifyToken] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [codesAcknowledged, setCodesAcknowledged] = useState(false);

  // Route protection: redirect if not authenticated or already has 2FA
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.twofa_enabled) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleStartSetup = async () => {
    try {
      setIsSubmitting(true);
      setError('');
      const response = await api.post('/api/auth/2fa/setup/');
      setQrCode(response.data.qr_code);
      setSecret(response.data.secret);
      setStep('scan');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to initialize 2FA setup');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      setError('');
      const response = await api.post('/api/auth/2fa/enable/', { token: verifyToken });
      setBackupCodes(response.data.backup_codes);
      setStep('backup');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Invalid verification code. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleComplete = async () => {
    // Refresh user data to update twofa_enabled status
    await refreshUser();
    setStep('complete');
  };

  const handleFinish = () => {
    navigate('/dashboard');
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

  const renderStepIndicator = () => {
    const steps = [
      { key: 'welcome', label: 'Start' },
      { key: 'scan', label: 'Scan' },
      { key: 'verify', label: 'Verify' },
      { key: 'backup', label: 'Backup' },
      { key: 'complete', label: 'Done' },
    ];

    const currentIndex = steps.findIndex(s => s.key === step);

    return (
      <div className="flex items-center justify-center mb-8">
        {steps.map((s, index) => (
          <React.Fragment key={s.key}>
            <div className="flex flex-col items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                  index < currentIndex
                    ? 'bg-green-500 text-white'
                    : index === currentIndex
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground'
                }`}
              >
                {index < currentIndex ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  index + 1
                )}
              </div>
              <span className="text-xs mt-1 text-muted-foreground">{s.label}</span>
            </div>
            {index < steps.length - 1 && (
              <div
                className={`w-12 h-0.5 mx-2 ${
                  index < currentIndex ? 'bg-green-500' : 'bg-muted'
                }`}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    );
  };

  const renderWelcomeStep = () => (
    <Card className="border-primary/20 shadow-xl max-w-lg mx-auto">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="bg-primary/10 p-4 rounded-full border border-primary/20">
            <Shield className="h-12 w-12 text-primary" />
          </div>
        </div>
        <CardTitle className="text-2xl">Secure Your Account</CardTitle>
        <CardDescription className="text-base">
          Two-factor authentication adds an extra layer of security to your account.
          You'll need to verify your identity using your phone when logging in.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
            <Smartphone className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <p className="font-medium text-sm">What you'll need</p>
              <p className="text-sm text-muted-foreground">
                An authenticator app like Google Authenticator, Authy, or Microsoft Authenticator
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
            <Key className="h-5 w-5 text-primary mt-0.5" />
            <div>
              <p className="font-medium text-sm">Backup codes</p>
              <p className="text-sm text-muted-foreground">
                You'll receive backup codes in case you lose access to your authenticator
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md border border-destructive/20 flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}

        <Button onClick={handleStartSetup} className="w-full" size="lg" disabled={isSubmitting}>
          {isSubmitting ? 'Setting up...' : 'Get Started'}
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </CardContent>
    </Card>
  );

  const renderScanStep = () => (
    <Card className="border-primary/20 shadow-xl max-w-lg mx-auto">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="bg-primary/10 p-4 rounded-full border border-primary/20">
            <QrCode className="h-12 w-12 text-primary" />
          </div>
        </div>
        <CardTitle className="text-2xl">Scan QR Code</CardTitle>
        <CardDescription className="text-base">
          Open your authenticator app and scan this QR code to add your account
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex justify-center p-4 bg-white rounded-lg">
          <img src={qrCode} alt="QR Code" className="w-48 h-48" />
        </div>

        <div className="space-y-2">
          <p className="text-sm font-medium text-center text-muted-foreground">
            Can't scan? Enter this code manually:
          </p>
          <div className="flex gap-2">
            <Input value={secret} readOnly className="font-mono text-center" />
            <Button variant="outline" onClick={() => copyToClipboard(secret)}>
              <Copy className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {success && (
          <div className="bg-green-500/10 text-green-600 text-sm p-2 rounded-md text-center">
            {success}
          </div>
        )}

        <Button onClick={() => setStep('verify')} className="w-full" size="lg">
          I've Scanned the Code
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </CardContent>
    </Card>
  );

  const renderVerifyStep = () => (
    <Card className="border-primary/20 shadow-xl max-w-lg mx-auto">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="bg-primary/10 p-4 rounded-full border border-primary/20">
            <Key className="h-12 w-12 text-primary" />
          </div>
        </div>
        <CardTitle className="text-2xl">Verify Setup</CardTitle>
        <CardDescription className="text-base">
          Enter the 6-digit code from your authenticator app to verify the setup
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleVerify} className="space-y-6">
          <div className="space-y-2">
            <Input
              type="text"
              placeholder="000000"
              value={verifyToken}
              onChange={(e) => setVerifyToken(e.target.value.replace(/\D/g, '').slice(0, 6))}
              className="text-center text-2xl tracking-widest font-mono"
              maxLength={6}
              disabled={isSubmitting}
              autoFocus
            />
            <p className="text-xs text-muted-foreground text-center">
              The code changes every 30 seconds
            </p>
          </div>

          {error && (
            <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md border border-destructive/20 flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              {error}
            </div>
          )}

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => setStep('scan')}
              className="flex-1"
              disabled={isSubmitting}
            >
              Back
            </Button>
            <Button
              type="submit"
              className="flex-1"
              size="lg"
              disabled={isSubmitting || verifyToken.length !== 6}
            >
              {isSubmitting ? 'Verifying...' : 'Verify'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );

  const renderBackupStep = () => (
    <Card className="border-yellow-500/50 bg-yellow-500/5 shadow-xl max-w-lg mx-auto">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="bg-yellow-500/10 p-4 rounded-full border border-yellow-500/20">
            <Key className="h-12 w-12 text-yellow-600" />
          </div>
        </div>
        <CardTitle className="text-2xl">Save Your Backup Codes</CardTitle>
        <CardDescription className="text-base">
          Save these codes in a secure location. You can use them to access your account
          if you lose your authenticator device. Each code can only be used once.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="bg-background p-4 rounded-lg border">
          <div className="grid grid-cols-2 gap-2 font-mono text-sm">
            {backupCodes.map((code, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-muted rounded"
              >
                <span>{code}</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(code)}
                  className="h-6 w-6 p-0"
                >
                  <Copy className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>

        <Button onClick={copyAllBackupCodes} variant="outline" className="w-full">
          <Copy className="h-4 w-4 mr-2" />
          Copy All Codes
        </Button>

        {success && (
          <div className="bg-green-500/10 text-green-600 text-sm p-2 rounded-md text-center">
            {success}
          </div>
        )}

        <div className="flex items-start gap-2">
          <input
            type="checkbox"
            id="acknowledge"
            checked={codesAcknowledged}
            onChange={(e) => setCodesAcknowledged(e.target.checked)}
            className="mt-1"
          />
          <label htmlFor="acknowledge" className="text-sm text-muted-foreground">
            I have saved my backup codes in a secure location
          </label>
        </div>

        <Button
          onClick={handleComplete}
          className="w-full"
          size="lg"
          disabled={!codesAcknowledged}
        >
          Continue
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </CardContent>
    </Card>
  );

  const renderCompleteStep = () => (
    <Card className="border-green-500/50 bg-green-500/5 shadow-xl max-w-lg mx-auto">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="bg-green-500/10 p-4 rounded-full border border-green-500/20">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
        </div>
        <CardTitle className="text-2xl">Setup Complete!</CardTitle>
        <CardDescription className="text-base">
          Two-factor authentication is now enabled on your account.
          You'll need to enter a code from your authenticator app each time you log in.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button onClick={handleFinish} className="w-full" size="lg">
          Go to Dashboard
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 p-4">
      <div className="w-full max-w-xl">
        {/* Logo and branding */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary/10 p-3 rounded-xl border border-primary/20">
              <Shield className="h-8 w-8 text-primary" />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-white mb-1">TechVault</h1>
          <p className="text-sm text-muted-foreground">Two-Factor Authentication Setup</p>
        </div>

        {renderStepIndicator()}

        {step === 'welcome' && renderWelcomeStep()}
        {step === 'scan' && renderScanStep()}
        {step === 'verify' && renderVerifyStep()}
        {step === 'backup' && renderBackupStep()}
        {step === 'complete' && renderCompleteStep()}
      </div>
    </div>
  );
};

export default TwoFactorSetup;
