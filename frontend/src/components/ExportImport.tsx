import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Download, Upload, Database, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { reportsAPI } from '@/services/core';
import { organizationAPI } from '@/services/core';
import { Organization } from '@/types/core';

interface ExportImportProps {
  isAdmin: boolean;
}

const ExportImport: React.FC<ExportImportProps> = ({ isAdmin }) => {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedOrgs, setSelectedOrgs] = useState<string[]>([]);
  const [exportAll, setExportAll] = useState(true);
  const [includeDeleted, setIncludeDeleted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingOrgs, setLoadingOrgs] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [overwriteExisting, setOverwriteExisting] = useState(false);
  const [importResult, setImportResult] = useState<{
    success: boolean;
    imported_organizations: string[];
    skipped_organizations: Array<{ name: string; reason: string }>;
    errors: Array<{ organization: string; error: string }>;
  } | null>(null);

  useEffect(() => {
    if (isAdmin) {
      loadOrganizations();
    }
  }, [isAdmin]);

  const loadOrganizations = async () => {
    setLoadingOrgs(true);
    try {
      const response = await organizationAPI.getAll({ page_size: 1000 });

      // Axios wraps the response in a data property
      // So response.data.results is the actual array
      let orgs: Organization[] = [];

      if (response.data && response.data.results) {
        // Standard paginated response: { data: { results: [...] } }
        orgs = response.data.results;
      } else if (Array.isArray(response.data)) {
        // Direct array in data
        orgs = response.data;
      } else if (Array.isArray(response)) {
        // Direct array
        orgs = response;
      }

      setOrganizations(orgs);
    } catch {
      setOrganizations([]);
    } finally {
      setLoadingOrgs(false);
    }
  };

  const handleExport = async () => {
    try {
      setLoading(true);
      const orgIds = exportAll ? undefined : selectedOrgs;

      const response = await reportsAPI.exportOrganizations(orgIds, includeDeleted);

      // Create a download link for the blob
      const blob = new Blob([response.data], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `organizations_export_${new Date().toISOString()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } } };
      alert(error.response?.data?.error || 'Failed to export organizations');
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!importFile) {
      alert('Please select a file to import');
      return;
    }

    try {
      setLoading(true);
      setImportResult(null);

      const result = await reportsAPI.importOrganizations(
        importFile,
        overwriteExisting,
        false // preserve_ids - usually false to avoid conflicts
      );

      setImportResult(result.data);
      setImportFile(null);

      // Reload organizations after import
      await loadOrganizations();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } } };
      alert(error.response?.data?.error || 'Failed to import organizations');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
        alert('Please select a JSON file');
        return;
      }
      setImportFile(file);
      setImportResult(null);
    }
  };

  const toggleOrgSelection = (orgId: string) => {
    setSelectedOrgs(prev =>
      prev.includes(orgId)
        ? prev.filter(id => id !== orgId)
        : [...prev, orgId]
    );
  };

  const toggleSelectAll = () => {
    if (selectedOrgs.length === (organizations?.length || 0)) {
      setSelectedOrgs([]);
    } else {
      setSelectedOrgs((organizations || []).map(org => org.id));
    }
  };

  if (!isAdmin) {
    return null;
  }

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          Organization Export / Import
        </CardTitle>
        <CardDescription>
          Export organizations as a backup or import previously exported data
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Export Section */}
          <div className="space-y-4">
            <div className="border border-border rounded-lg p-4">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Download className="h-5 w-5 text-primary" />
                Export Organizations
              </h3>

              <div className="space-y-4">
                {/* Export All or Selected */}
                <div className="space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={exportAll}
                      onChange={() => setExportAll(true)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm font-medium">Export All Organizations</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      checked={!exportAll}
                      onChange={() => setExportAll(false)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm font-medium">Select Organizations</span>
                  </label>
                </div>

                {/* Organization Selection */}
                {!exportAll && (
                  <div className="border border-border rounded p-3 max-h-64 overflow-y-auto space-y-2">
                    <div className="flex items-center justify-between mb-2 pb-2 border-b border-border">
                      <span className="text-sm font-medium">
                        {selectedOrgs.length} of {organizations?.length || 0} selected
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={toggleSelectAll}
                        disabled={loadingOrgs || (organizations?.length || 0) === 0}
                      >
                        {selectedOrgs.length === (organizations?.length || 0) ? 'Deselect All' : 'Select All'}
                      </Button>
                    </div>
                    {loadingOrgs ? (
                      <div className="text-center py-4 text-sm text-muted-foreground">
                        Loading organizations...
                      </div>
                    ) : (organizations || []).length === 0 ? (
                      <div className="text-center py-4 text-sm text-muted-foreground">
                        No organizations found
                      </div>
                    ) : (
                      (organizations || []).map(org => (
                        <label key={org.id} className="flex items-center gap-2 cursor-pointer hover:bg-muted/50 p-2 rounded">
                          <input
                            type="checkbox"
                            checked={selectedOrgs.includes(org.id)}
                            onChange={() => toggleOrgSelection(org.id)}
                            className="w-4 h-4"
                          />
                          <span className="text-sm">{org.name}</span>
                        </label>
                      ))
                    )}
                  </div>
                )}

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

                {/* Export Button */}
                <Button
                  onClick={handleExport}
                  disabled={loading || (!exportAll && selectedOrgs.length === 0)}
                  className="w-full"
                >
                  <Download className="h-4 w-4 mr-2" />
                  {loading ? 'Exporting...' : 'Export to JSON'}
                </Button>

                <p className="text-xs text-muted-foreground">
                  This will download a JSON file containing all data for the selected organizations, including locations, contacts, devices, and all other related records.
                </p>
              </div>
            </div>
          </div>

          {/* Import Section */}
          <div className="space-y-4">
            <div className="border border-border rounded-lg p-4">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Upload className="h-5 w-5 text-primary" />
                Import Organizations
              </h3>

              <div className="space-y-4">
                {/* File Upload */}
                <div className="space-y-2">
                  <label htmlFor="import-file" className="text-sm font-medium block">
                    Select Export File
                  </label>
                  <input
                    id="import-file"
                    type="file"
                    accept=".json,application/json"
                    onChange={handleFileChange}
                    className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90 cursor-pointer"
                  />
                  {importFile && (
                    <p className="text-xs text-muted-foreground">
                      Selected: {importFile.name}
                    </p>
                  )}
                </div>

                {/* Import Options */}
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={overwriteExisting}
                    onChange={(e) => setOverwriteExisting(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">Overwrite existing organizations</span>
                </label>

                {/* Import Button */}
                <Button
                  onClick={handleImport}
                  disabled={loading || !importFile}
                  className="w-full"
                  variant="default"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  {loading ? 'Importing...' : 'Import from JSON'}
                </Button>

                <div className="bg-amber-500/10 text-amber-600 dark:text-amber-400 text-xs p-3 rounded-md border border-amber-500/20">
                  <AlertCircle className="h-4 w-4 inline mr-1" />
                  <strong>Warning:</strong> Importing will create new organizations and all their related data. This operation cannot be easily undone.
                </div>

                {/* Import Result */}
                {importResult && (
                  <div className={`p-4 rounded-lg border ${
                    importResult.success
                      ? 'bg-green-500/10 border-green-500/20 text-green-600 dark:text-green-400'
                      : 'bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400'
                  }`}>
                    <div className="flex items-start gap-2 mb-2">
                      {importResult.success ? (
                        <CheckCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <p className="font-semibold mb-2">
                          {importResult.success ? 'Import Completed' : 'Import Failed'}
                        </p>

                        {importResult.imported_organizations.length > 0 && (
                          <div className="mb-2">
                            <p className="text-sm font-medium mb-1">
                              Imported ({importResult.imported_organizations.length}):
                            </p>
                            <ul className="text-xs list-disc list-inside">
                              {importResult.imported_organizations.map((org, idx) => (
                                <li key={idx}>{org}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {importResult.skipped_organizations.length > 0 && (
                          <div className="mb-2">
                            <p className="text-sm font-medium mb-1">
                              Skipped ({importResult.skipped_organizations.length}):
                            </p>
                            <ul className="text-xs list-disc list-inside">
                              {importResult.skipped_organizations.map((item, idx) => (
                                <li key={idx}>{item.name}: {item.reason}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {importResult.errors.length > 0 && (
                          <div>
                            <p className="text-sm font-medium mb-1">
                              Errors ({importResult.errors.length}):
                            </p>
                            <ul className="text-xs list-disc list-inside">
                              {importResult.errors.map((item, idx) => (
                                <li key={idx}>{item.organization}: {item.error}</li>
                              ))}
                            </ul>
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

export default ExportImport;
