import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Organization } from '../types/core';
import { organizationAPI } from '../services/core';
import { useAuth } from './AuthContext';

interface OrganizationContextType {
  selectedOrg: Organization | null;
  setSelectedOrg: (org: Organization | null) => void;
  organizations: Organization[];
  loading: boolean;
  error: string | null;
  refreshOrganizations: () => Promise<void>;
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined);

const SELECTED_ORG_KEY = 'techvault_selected_org';

export const OrganizationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const [selectedOrg, setSelectedOrgState] = useState<Organization | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadOrganizations = async () => {
    // Only load organizations if user is authenticated
    if (!isAuthenticated) {
      setOrganizations([]);
      setSelectedOrgState(null);
      setLoading(false);
      setError(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await organizationAPI.getAll();
      const orgs = response.data?.results || [];
      setOrganizations(orgs);

      // Try to restore previously selected org from localStorage
      const savedOrgId = localStorage.getItem(SELECTED_ORG_KEY);
      if (savedOrgId) {
        const savedOrg = orgs.find((org: Organization) => org.id.toString() === savedOrgId);
        if (savedOrg) {
          setSelectedOrgState(savedOrg);
        } else {
          // Saved org no longer exists, clear it
          localStorage.removeItem(SELECTED_ORG_KEY);
        }
      }
    } catch (error) {
      console.error('Failed to load organizations:', error);
      setError('Failed to load organizations');
      setOrganizations([]);
    } finally {
      setLoading(false);
    }
  };

  // Load organizations when authentication state changes
  useEffect(() => {
    loadOrganizations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  const setSelectedOrg = (org: Organization | null) => {
    setSelectedOrgState(org);
    if (org) {
      localStorage.setItem(SELECTED_ORG_KEY, org.id.toString());
    } else {
      localStorage.removeItem(SELECTED_ORG_KEY);
    }
  };

  const refreshOrganizations = async () => {
    await loadOrganizations();
  };

  return (
    <OrganizationContext.Provider
      value={{
        selectedOrg,
        setSelectedOrg,
        organizations,
        loading,
        error,
        refreshOrganizations,
      }}
    >
      {children}
    </OrganizationContext.Provider>
  );
};

export const useOrganization = (): OrganizationContextType => {
  const context = useContext(OrganizationContext);
  if (context === undefined) {
    throw new Error('useOrganization must be used within an OrganizationProvider');
  }
  return context;
};
