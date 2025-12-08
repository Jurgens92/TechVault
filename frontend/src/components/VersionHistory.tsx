import React, { useState, useEffect } from 'react';
import {
  DocumentationVersion,
  PasswordEntryVersion,
  ConfigurationVersion,
} from '../types/core';

type Version = DocumentationVersion | PasswordEntryVersion | ConfigurationVersion;

interface VersionHistoryProps<T extends Version> {
  entryId: string;
  getVersions: (id: string) => Promise<{ data: T[] }>;
  restoreVersion: (id: string, versionNumber: number) => Promise<any>;
  onRestore?: () => void;
  renderVersionDetails: (version: T) => React.ReactNode;
}

export function VersionHistory<T extends Version>({
  entryId,
  getVersions,
  restoreVersion,
  onRestore,
  renderVersionDetails,
}: VersionHistoryProps<T>) {
  const [versions, setVersions] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<T | null>(null);
  const [restoring, setRestoring] = useState(false);

  useEffect(() => {
    loadVersions();
  }, [entryId]);

  const loadVersions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getVersions(entryId);
      setVersions(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load version history');
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (versionNumber: number) => {
    if (!confirm(`Are you sure you want to restore to version ${versionNumber}?`)) {
      return;
    }

    try {
      setRestoring(true);
      await restoreVersion(entryId, versionNumber);
      alert(`Successfully restored to version ${versionNumber}`);
      if (onRestore) {
        onRestore();
      }
      loadVersions();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to restore version');
    } finally {
      setRestoring(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="p-4">
        <p className="text-gray-600">Loading version history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (versions.length === 0) {
    return (
      <div className="p-4">
        <p className="text-gray-600">No version history available yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Version History</h3>

      <div className="space-y-3">
        {versions.map((version) => (
          <div
            key={version.id}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
          >
            <div className="flex justify-between items-start mb-2">
              <div>
                <h4 className="font-medium text-gray-900">
                  Version {version.version_number}
                </h4>
                <p className="text-sm text-gray-600">
                  {formatDate(version.created_at)}
                  {version.created_by && (
                    <span className="ml-2">
                      by {version.created_by.email}
                    </span>
                  )}
                </p>
                {version.change_note && (
                  <p className="text-sm text-gray-700 mt-1 italic">
                    "{version.change_note}"
                  </p>
                )}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() =>
                    setSelectedVersion(
                      selectedVersion?.id === version.id ? null : version
                    )
                  }
                  className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded"
                >
                  {selectedVersion?.id === version.id ? 'Hide' : 'View'}
                </button>
                <button
                  onClick={() => handleRestore(version.version_number)}
                  disabled={restoring}
                  className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded disabled:opacity-50"
                >
                  Restore
                </button>
              </div>
            </div>

            {selectedVersion?.id === version.id && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                {renderVersionDetails(version)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
