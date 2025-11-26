import api from './api';
import {
  Organization, Location, Contact, Documentation,
  PasswordEntry, Configuration, PaginatedResponse
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
};
