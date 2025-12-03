import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Shield, KeyRound } from 'lucide-react';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [twofaToken, setTwofaToken] = useState('');
  const [requires2FA, setRequires2FA] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const credentials: any = { email, password };
      if (requires2FA && twofaToken) {
        credentials.twofa_token = twofaToken;
      }

      const result = await login(credentials);

      // Check if 2FA is required
      if (result && result.requires_2fa) {
        setRequires2FA(true);
        setError('');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.response?.data?.non_field_errors?.[0] || 'Login failed. Please check your credentials.');
      // Reset 2FA token on error
      setTwofaToken('');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setRequires2FA(false);
    setTwofaToken('');
    setError('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 p-4">
      <div className="w-full max-w-md">
        {/* Logo and branding */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary/10 p-3 rounded-xl border border-primary/20">
              <Shield className="h-10 w-10 text-primary" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">TechVault</h1>
          <p className="text-muted-foreground">Enterprise IT Documentation Platform</p>
        </div>

        <Card className="border-primary/20 shadow-xl">
          <CardHeader>
            <CardTitle>{requires2FA ? 'Two-Factor Authentication' : 'Welcome back'}</CardTitle>
            <CardDescription>
              {requires2FA
                ? 'Enter your 6-digit authentication code or a backup code'
                : 'Sign in to your account to continue'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-md border border-destructive/20">
                  {error}
                </div>
              )}

              {!requires2FA ? (
                <>
                  <div className="space-y-2">
                    <label htmlFor="email" className="text-sm font-medium">
                      Email
                    </label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@company.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      disabled={loading}
                    />
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="password" className="text-sm font-medium">
                      Password
                    </label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      disabled={loading}
                    />
                  </div>
                </>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-center p-4 bg-primary/5 rounded-lg border border-primary/20">
                    <KeyRound className="h-8 w-8 text-primary" />
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="twofa-token" className="text-sm font-medium">
                      Authentication Code
                    </label>
                    <Input
                      id="twofa-token"
                      type="text"
                      placeholder="000000 or backup code"
                      value={twofaToken}
                      onChange={(e) => setTwofaToken(e.target.value)}
                      required
                      disabled={loading}
                      autoFocus
                      maxLength={50}
                    />
                    <p className="text-xs text-muted-foreground">
                      Enter the 6-digit code from your authenticator app or use a backup code.
                    </p>
                  </div>

                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleBack}
                    disabled={loading}
                    className="w-full"
                  >
                    Back to login
                  </Button>
                </div>
              )}

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Verifying...' : requires2FA ? 'Verify' : 'Sign in'}
              </Button>
            </form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
             
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-muted-foreground mt-8">
          Secure authentication powered by TechVault
        </p>
      </div>
    </div>
  );
};

export default Login;
