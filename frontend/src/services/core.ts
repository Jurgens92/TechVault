import api from './api';
import {
  Organization, Location, Contact, Documentation,
  PasswordEntry, Configuration, NetworkDevice, EndpointUser,
  Server, Peripheral, Software, Backup, VoIP, DiagramData, PaginatedResponse,
  DocumentationVersion, PasswordEntryVersion, ConfigurationVersion
} from '../types/core';

// Dashboard APIs
export const dashboardAPI = {
  getStats: () =>
    api.get<{
      organizations: number;
      locations: number;
      contacts: number;
      documentations: number;
      passwords: number;
      configurations: number;
    }>('/api/dashboard/stats/'),
};

// Endpoints page APIs
export interface EndpointCounts {
  network_devices: number;
  endpoint_users: number;
  servers: number;
  peripherals: number;
  backups: number;
  software: number;
  voip: number;
}

export const endpointsAPI = {
  getCounts: (organizationId: string) =>
    api.get<EndpointCounts>('/api/endpoints/counts/', {
      params: { organization_id: organizationId }
    }),
};

// Organization APIs
export const organizationAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Organization>>('/api/organizations/', { params }),
  getById: (id: string) =>
    api.get<Organization>(`/api/organizations/${id}/`),
  create: (data: Partial<Organization>) =>
    api.post<Organization>('/api/organizations/', data),
  update: (id: string, data: Partial<Organization>) =>
    api.patch<Organization>(`/api/organizations/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/organizations/${id}/`),
  search: (q: string) =>
    api.get<Organization[]>('/api/organizations/search/', { params: { q } }),
  getStats: (id: string) =>
    api.get(`/api/organizations/${id}/stats/`),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Organization>>('/api/organizations/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/organizations/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/organizations/${id}/hard_delete/`),
};

// Location APIs
export const locationAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Location>>('/api/locations/', { params }),
  getById: (id: string) =>
    api.get<Location>(`/api/locations/${id}/`),
  create: (data: Partial<Location>) =>
    api.post<Location>('/api/locations/', data),
  update: (id: string, data: Partial<Location>) =>
    api.patch<Location>(`/api/locations/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/locations/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<Location[]>('/api/locations/by_organization/', { params: { organization_id: organizationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Location>>('/api/locations/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/locations/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/locations/${id}/hard_delete/`),
};

// Contact APIs
export const contactAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Contact>>('/api/contacts/', { params }),
  getById: (id: string) =>
    api.get<Contact>(`/api/contacts/${id}/`),
  create: (data: Partial<Contact>) =>
    api.post<Contact>('/api/contacts/', data),
  update: (id: string, data: Partial<Contact>) =>
    api.patch<Contact>(`/api/contacts/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/contacts/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<Contact[]>('/api/contacts/by_organization/', { params: { organization_id: organizationId } }),
  byLocation: (locationId: string) =>
    api.get<Contact[]>('/api/contacts/by_location/', { params: { location_id: locationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Contact>>('/api/contacts/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/contacts/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/contacts/${id}/hard_delete/`),
  downloadExampleCSV: () => {
    return api.get('/api/contacts/download_example_csv/', {
      responseType: 'blob'
    });
  },
  importCSV: (file: File, organizationId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('organization_id', organizationId);
    return api.post<{
      created: number;
      errors: Array<{ row: number; error: string }>;
      message: string;
    }>('/api/contacts/import_csv/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// Documentation APIs
export const documentationAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Documentation>>('/api/documentations/', { params }),
  getById: (id: string) =>
    api.get<Documentation>(`/api/documentations/${id}/`),
  create: (data: Partial<Documentation>) =>
    api.post<Documentation>('/api/documentations/', data),
  update: (id: string, data: Partial<Documentation>) =>
    api.patch<Documentation>(`/api/documentations/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/documentations/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<Documentation[]>('/api/documentations/by_organization/', { params: { organization_id: organizationId } }),
  publish: (id: string) =>
    api.post(`/api/documentations/${id}/publish/`, {}),
  unpublish: (id: string) =>
    api.post(`/api/documentations/${id}/unpublish/`, {}),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Documentation>>('/api/documentations/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/documentations/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/documentations/${id}/hard_delete/`),
  // Version history
  getVersions: (id: string) =>
    api.get<DocumentationVersion[]>(`/api/documentations/${id}/versions/`),
  getVersion: (id: string, versionNumber: number) =>
    api.get<DocumentationVersion>(`/api/documentations/${id}/versions/${versionNumber}/`),
  restoreVersion: (id: string, versionNumber: number) =>
    api.post<{ detail: string; data: Documentation }>(`/api/documentations/${id}/restore-version/${versionNumber}/`, {}),
};

// Password Entry APIs
export const passwordAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<PasswordEntry>>('/api/passwords/', { params }),
  getById: (id: string) =>
    api.get<PasswordEntry>(`/api/passwords/${id}/`),
  create: (data: Partial<PasswordEntry>) =>
    api.post<PasswordEntry>('/api/passwords/', data),
  update: (id: string, data: Partial<PasswordEntry>) =>
    api.patch<PasswordEntry>(`/api/passwords/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/passwords/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<PasswordEntry[]>('/api/passwords/by_organization/', { params: { organization_id: organizationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<PasswordEntry>>('/api/passwords/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/passwords/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/passwords/${id}/hard_delete/`),
  // Version history
  getVersions: (id: string) =>
    api.get<PasswordEntryVersion[]>(`/api/passwords/${id}/versions/`),
  getVersion: (id: string, versionNumber: number) =>
    api.get<PasswordEntryVersion>(`/api/passwords/${id}/versions/${versionNumber}/`),
  restoreVersion: (id: string, versionNumber: number) =>
    api.post<{ detail: string; data: PasswordEntry }>(`/api/passwords/${id}/restore-version/${versionNumber}/`, {}),
  // Securely retrieve the decrypted password (with audit logging)
  retrievePassword: (id: string) =>
    api.post<{ password: string; warning: string }>(`/api/passwords/${id}/retrieve_password/`),
};

// Configuration APIs
export const configurationAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Configuration>>('/api/configurations/', { params }),
  getById: (id: string) =>
    api.get<Configuration>(`/api/configurations/${id}/`),
  create: (data: Partial<Configuration>) =>
    api.post<Configuration>('/api/configurations/', data),
  update: (id: string, data: Partial<Configuration>) =>
    api.patch<Configuration>(`/api/configurations/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/configurations/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<Configuration[]>('/api/configurations/by_organization/', { params: { organization_id: organizationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Configuration>>('/api/configurations/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/configurations/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/configurations/${id}/hard_delete/`),
  // Version history
  getVersions: (id: string) =>
    api.get<ConfigurationVersion[]>(`/api/configurations/${id}/versions/`),
  getVersion: (id: string, versionNumber: number) =>
    api.get<ConfigurationVersion>(`/api/configurations/${id}/versions/${versionNumber}/`),
  restoreVersion: (id: string, versionNumber: number) =>
    api.post<{ detail: string; data: Configuration }>(`/api/configurations/${id}/restore-version/${versionNumber}/`, {}),
};

// Network Device APIs
export const networkDeviceAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<NetworkDevice>>('/api/network-devices/', { params }),
  getById: (id: string) =>
    api.get<NetworkDevice>(`/api/network-devices/${id}/`),
  create: (data: Partial<NetworkDevice>) =>
    api.post<NetworkDevice>('/api/network-devices/', data),
  update: (id: string, data: Partial<NetworkDevice>) =>
    api.patch<NetworkDevice>(`/api/network-devices/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/network-devices/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<NetworkDevice[]>('/api/network-devices/by_organization/', { params: { organization_id: organizationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<NetworkDevice>>('/api/network-devices/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/network-devices/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/network-devices/${id}/hard_delete/`),
};

// Endpoint User APIs
export const endpointUserAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<EndpointUser>>('/api/endpoint-users/', { params }),
  getById: (id: string) =>
    api.get<EndpointUser>(`/api/endpoint-users/${id}/`),
  create: (data: Partial<EndpointUser>) =>
    api.post<EndpointUser>('/api/endpoint-users/', data),
  update: (id: string, data: Partial<EndpointUser>) =>
    api.patch<EndpointUser>(`/api/endpoint-users/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/endpoint-users/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<EndpointUser[]>('/api/endpoint-users/by_organization/', { params: { organization_id: organizationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<EndpointUser>>('/api/endpoint-users/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/endpoint-users/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/endpoint-users/${id}/hard_delete/`),
  downloadExampleCSV: () => {
    return api.get('/api/endpoint-users/download_example_csv/', {
      responseType: 'blob'
    });
  },
  importCSV: (file: File, organizationId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('organization_id', organizationId);
    return api.post<{
      created: number;
      errors: Array<{ row: number; error: string }>;
      message: string;
    }>('/api/endpoint-users/import_csv/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// Server APIs
export const serverAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Server>>('/api/servers/', { params }),
  getById: (id: string) =>
    api.get<Server>(`/api/servers/${id}/`),
  create: (data: Partial<Server>) =>
    api.post<Server>('/api/servers/', data),
  update: (id: string, data: Partial<Server>) =>
    api.patch<Server>(`/api/servers/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/servers/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<Server[]>('/api/servers/by_organization/', { params: { organization_id: organizationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Server>>('/api/servers/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/servers/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/servers/${id}/hard_delete/`),
};

// Peripheral APIs
export const peripheralAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Peripheral>>('/api/peripherals/', { params }),
  getById: (id: string) =>
    api.get<Peripheral>(`/api/peripherals/${id}/`),
  create: (data: Partial<Peripheral>) =>
    api.post<Peripheral>('/api/peripherals/', data),
  update: (id: string, data: Partial<Peripheral>) =>
    api.patch<Peripheral>(`/api/peripherals/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/peripherals/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<Peripheral[]>('/api/peripherals/by_organization/', { params: { organization_id: organizationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Peripheral>>('/api/peripherals/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/peripherals/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/peripherals/${id}/hard_delete/`),
};

// Software APIs
export const softwareAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Software>>('/api/software/', { params }),
  getById: (id: string) =>
    api.get<Software>(`/api/software/${id}/`),
  create: (data: Partial<Software>) =>
    api.post<Software>('/api/software/', data),
  update: (id: string, data: Partial<Software>) =>
    api.patch<Software>(`/api/software/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/software/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<Software[]>('/api/software/by_organization/', { params: { organization_id: organizationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Software>>('/api/software/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/software/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/software/${id}/hard_delete/`),
};

// Backup APIs
export const backupAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Backup>>('/api/backups/', { params }),
  getById: (id: string) =>
    api.get<Backup>(`/api/backups/${id}/`),
  create: (data: Partial<Backup>) =>
    api.post<Backup>('/api/backups/', data),
  update: (id: string, data: Partial<Backup>) =>
    api.patch<Backup>(`/api/backups/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/backups/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<Backup[]>('/api/backups/by_organization/', { params: { organization_id: organizationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Backup>>('/api/backups/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/backups/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/backups/${id}/hard_delete/`),
};

// VoIP APIs
export const voipAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<VoIP>>('/api/voip/', { params }),
  getById: (id: string) =>
    api.get<VoIP>(`/api/voip/${id}/`),
  create: (data: Partial<VoIP>) =>
    api.post<VoIP>('/api/voip/', data),
  update: (id: string, data: Partial<VoIP>) =>
    api.patch<VoIP>(`/api/voip/${id}/`, data),
  delete: (id: string) =>
    api.delete(`/api/voip/${id}/`),
  byOrganization: (organizationId: string) =>
    api.get<VoIP[]>('/api/voip/by_organization/', { params: { organization_id: organizationId } }),
  getDeleted: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<VoIP>>('/api/voip/deleted/', { params }),
  restore: (id: string) =>
    api.post(`/api/voip/${id}/restore/`, {}),
  hardDelete: (id: string) =>
    api.delete(`/api/voip/${id}/hard_delete/`),
};

// Diagram APIs
export const diagramAPI = {
  getData: (organizationId?: string, locationId?: string) => {
    const params: Record<string, string> = {};
    if (organizationId) params.organization_id = organizationId;
    if (locationId) params.location_id = locationId;
    return api.get<DiagramData>('/api/diagram/data/', { params: Object.keys(params).length > 0 ? params : undefined });
  },
};

// Reports / Export/Import APIs
export const reportsAPI = {
  exportOrganizations: (organizationIds?: string[], includeDeleted: boolean = false) =>
    api.post('/api/reports/export-organizations/', {
      organization_ids: organizationIds,
      include_deleted: includeDeleted
    }, {
      responseType: 'blob'
    }),
  importOrganizations: (file: File, overwriteExisting: boolean = false, preserveIds: boolean = false) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('overwrite_existing', overwriteExisting.toString());
    formData.append('preserve_ids', preserveIds.toString());
    return api.post<{
      success: boolean;
      imported_organizations: string[];
      skipped_organizations: Array<{ name: string; reason: string }>;
      errors: Array<{ organization: string; error: string }>;
    }>('/api/reports/import-organizations/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  // System Backup & Restore APIs
  createSystemBackup: (includeDeleted: boolean = false) =>
    api.post('/api/reports/system-backup/', {
      include_deleted: includeDeleted
    }, {
      responseType: 'blob'
    }),
  restoreSystemBackup: (
    file: File,
    options: {
      restoreUsers?: boolean;
      restoreOrganizations?: boolean;
      overwriteExisting?: boolean;
    } = {}
  ) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('restore_users', (options.restoreUsers ?? true).toString());
    formData.append('restore_organizations', (options.restoreOrganizations ?? true).toString());
    formData.append('overwrite_existing', (options.overwriteExisting ?? false).toString());
    return api.post<{
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
    }>('/api/reports/system-restore/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
};
