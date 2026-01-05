import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Download, Upload, HardDrive, CheckCircle, XCircle, AlertTriangle, Users, Building2, Shield } from 'lucide-react';
import { reportsAPI } from '@/services/core';

interface BackupRestoreProps {
  isAdmin: boolean;
}

interface RestoreResult {
  success: boolean;
  users: {
    restored: Array<{ email: string; action: string }>;
    skipped: Array<{ email: string; reason: string }>;
    errors: Array<{ email: string; error: string }>;
  };
  organizations: {
    imported: string[];
    skipped: Array<{ name: string; reason: string }>;
    errors: Array<{ organization: string; error: string }>;
  };
}

const BackupRestore: React.FC<BackupRestoreProps> = ({ isAdmin }) => {
  const [loading, setLoading] = useState(false);
  const [includeDeleted, setIncludeDeleted] = useState(false);
  const [restoreFile, setRestoreFile] = useState<File | null>(null);
  const [restoreUsers, setRestoreUsers] = useState(true);
  const [restoreOrganizations, setRestoreOrganizations] = useState(true);
  const [overwriteExisting, setOverwriteExisting] = useState(false);
  const [restoreResult, setRestoreResult] = useState<RestoreResult | null>(null);

  const handleBackup = async () => {
    try {
      setLoading(true);
      const response = await reportsAPI.createSystemBackup(includeDeleted);

      // Create a download link for the blob
      const blob = new Blob([response.data], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `techvault_system_backup_${new Date().toISOString()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to create backup');
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async () => {
    if (!restoreFile) {
      alert('Please select a backup file to restore');
      return;
    }

    if (!restoreUsers && !restoreOrganizations) {
      alert('Please select at least one data type to restore');
      return;
    }

    // Confirm before restore
    const confirmMessage = overwriteExisting
      ? 'WARNING: This will overwrite existing data. Are you sure you want to proceed with the restore?'
      : 'Are you sure you want to restore from this backup?';

    if (!confirm(confirmMessage)) {
      return;
    }

    try {
      setLoading(true);
      setRestoreResult(null);

      const result = await reportsAPI.restoreSystemBackup(restoreFile, {
        restoreUsers,
        restoreOrganizations,
        overwriteExisting,
      });

      setRestoreResult(result.data);
      setRestoreFile(null);
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to restore backup');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
        alert('Please select a JSON backup file');
        return;
      }
      setRestoreFile(file);
      setRestoreResult(null);
    }
  };

  if (!isAdmin) {
    return null;
  }

  const totalRestored = (restoreResult?.users.restored.length || 0) + (restoreResult?.organizations.imported.length || 0);
  const totalSkipped = (restoreResult?.users.skipped.length || 0) + (restoreResult?.organizations.skipped.length || 0);
  const totalErrors = (restoreResult?.users.errors.length || 0) + (restoreResult?.organizations.errors.length || 0);

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <HardDrive className="h-5 w-5" />
          System Backup & Restore
        </CardTitle>
        <CardDescription>
          Create a complete system backup including all users, organizations, passwords, and 2FA configurations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Backup Section */}
          <div className="space-y-4">
            <div className="border border-border rounded-lg p-4">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Download className="h-5 w-5 text-primary" />
                Create Backup
              </h3>

              <div className="space-y-4">
                <div className="bg-muted/50 rounded-lg p-4 space-y-3">
                  <p className="text-sm font-medium">This backup will include:</p>
                  <ul className="text-sm text-muted-foreground space-y-2">
                    <li className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-primary" />
                      All user accounts with password hashes
                    </li>
                    <li className="flex items-center gap-2">
                      <Shield className="h-4 w-4 text-primary" />
                      2FA secrets and backup codes
                    </li>
                    <li className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-primary" />
                      All organizations and related data
                    </li>
                  </ul>
                </div>

                {/* Include Deleted */}
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeDeleted}
                    onChange={(e) => setIncludeDeleted(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">Include soft-deleted records</span>
                </label>

                {/* Backup Button */}
                <Button
                  onClick={handleBackup}
                  disabled={loading}
                  className="w-full"
                >
                  <Download className="h-4 w-4 mr-2" />
                  {loading ? 'Creating Backup...' : 'Download System Backup'}
                </Button>

                <p className="text-xs text-muted-foreground">
                  The backup file will contain sensitive data including password hashes and 2FA secrets. Store it securely.
                </p>
              </div>
            </div>
          </div>

          {/* Restore Section */}
          <div className="space-y-4">
            <div className="border border-border rounded-lg p-4">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Upload className="h-5 w-5 text-primary" />
                Restore from Backup
              </h3>

              <div className="space-y-4">
                {/* File Upload */}
                <div className="space-y-2">
                  <label htmlFor="restore-file" className="text-sm font-medium block">
                    Select Backup File
                  </label>
                  <input
                    id="restore-file"
                    type="file"
                    accept=".json,application/json"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90 cursor-pointer"
                  />
                  {restoreFile && (
                    <p className="text-xs text-muted-foreground">
                      Selected: {restoreFile.name}
                    </p>
                  )}
                </div>

                {/* Restore Options */}
                <div className="space-y-2">
                  <p className="text-sm font-medium">Data to restore:</p>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={restoreUsers}
                      onChange={(e) => setRestoreUsers(e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Users (accounts, passwords, 2FA)</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={restoreOrganizations}
                      onChange={(e) => setRestoreOrganizations(e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Organizations (all related data)</span>
                  </label>
                </div>

                {/* Overwrite Option */}
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={overwriteExisting}
                    onChange={(e) => setOverwriteExisting(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">Overwrite existing records</span>
                </label>

                {/* Restore Button */}
                <Button
                  onClick={handleRestore}
                  disabled={loading || !restoreFile || (!restoreUsers && !restoreOrganizations)}
                  className="w-full"
                  variant="default"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  {loading ? 'Restoring...' : 'Restore from Backup'}
                </Button>

                <div className="bg-amber-500/10 text-amber-600 dark:text-amber-400 text-xs p-3 rounded-md border border-amber-500/20">
                  <AlertTriangle className="h-4 w-4 inline mr-1" />
                  <strong>Warning:</strong> Restoring will modify your system data. Ensure you have a current backup before proceeding.
                </div>

                {/* Restore Result */}
                {restoreResult && (
                  <div className={`p-4 rounded-lg border ${
                    restoreResult.success
                      ? 'bg-green-500/10 border-green-500/20 text-green-600 dark:text-green-400'
                      : 'bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400'
                  }`}>
                    <div className="flex items-start gap-2 mb-2">
                      {restoreResult.success ? (
                        <CheckCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <p className="font-semibold mb-2">
                          {restoreResult.success ? 'Restore Completed' : 'Restore Completed with Errors'}
                        </p>

                        {/* Summary */}
                        <div className="text-xs mb-3 space-y-1">
                          <p>Restored: {totalRestored} | Skipped: {totalSkipped} | Errors: {totalErrors}</p>
                        </div>

                        {/* Users Section */}
                        {restoreUsers && (
                          <div className="mb-3">
                            <p className="text-sm font-medium mb-1 flex items-center gap-1">
                              <Users className="h-3 w-3" /> Users
                            </p>

                            {restoreResult.users.restored.length > 0 && (
                              <div className="mb-2">
                                <p className="text-xs font-medium">
                                  Restored ({restoreResult.users.restored.length}):
                                </p>
                                <ul className="text-xs list-disc list-inside max-h-20 overflow-y-auto">
                                  {restoreResult.users.restored.map((user, idx) => (
                                    <li key={idx}>{user.email} ({user.action})</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {restoreResult.users.skipped.length > 0 && (
                              <div className="mb-2">
                                <p className="text-xs font-medium">
                                  Skipped ({restoreResult.users.skipped.length}):
                                </p>
                                <ul className="text-xs list-disc list-inside max-h-20 overflow-y-auto">
                                  {restoreResult.users.skipped.map((item, idx) => (
                                    <li key={idx}>{item.email}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {restoreResult.users.errors.length > 0 && (
                              <div>
                                <p className="text-xs font-medium text-red-500">
                                  Errors ({restoreResult.users.errors.length}):
                                </p>
                                <ul className="text-xs list-disc list-inside max-h-20 overflow-y-auto text-red-500">
                                  {restoreResult.users.errors.map((item, idx) => (
                                    <li key={idx}>{item.email}: {item.error}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Organizations Section */}
                        {restoreOrganizations && (
                          <div>
                            <p className="text-sm font-medium mb-1 flex items-center gap-1">
                              <Building2 className="h-3 w-3" /> Organizations
                            </p>

                            {restoreResult.organizations.imported.length > 0 && (
                              <div className="mb-2">
                                <p className="text-xs font-medium">
                                  Imported ({restoreResult.organizations.imported.length}):
                                </p>
                                <ul className="text-xs list-disc list-inside max-h-20 overflow-y-auto">
                                  {restoreResult.organizations.imported.map((org, idx) => (
                                    <li key={idx}>{org}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {restoreResult.organizations.skipped.length > 0 && (
                              <div className="mb-2">
                                <p className="text-xs font-medium">
                                  Skipped ({restoreResult.organizations.skipped.length}):
                                </p>
                                <ul className="text-xs list-disc list-inside max-h-20 overflow-y-auto">
                                  {restoreResult.organizations.skipped.map((item, idx) => (
                                    <li key={idx}>{item.name}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {restoreResult.organizations.errors.length > 0 && (
                              <div>
                                <p className="text-xs font-medium text-red-500">
                                  Errors ({restoreResult.organizations.errors.length}):
                                </p>
                                <ul className="text-xs list-disc list-inside max-h-20 overflow-y-auto text-red-500">
                                  {restoreResult.organizations.errors.map((item, idx) => (
                                    <li key={idx}>{item.organization}: {item.error}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default BackupRestore;
