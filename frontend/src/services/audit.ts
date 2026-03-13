import api from './api';

export interface AuditChangeField {
  field: string;
  value: any;
}

export interface AuditChangeDiff {
  field: string;
  old: any;
  new: any;
}

export interface AuditChanges {
  fields?: AuditChangeField[];
  diff?: AuditChangeDiff[];
}

export interface AuditLogEntry {
  id: string;
  user: number | null;
  user_email: string;
  user_name: string;
  action: 'create' | 'update' | 'delete' | 'restore' | 'export' | 'import' | 'login' | 'logout';
  entity_type: string;
  entity_id: string;
  entity_name: string;
  organization_name: string;
  details: string;
  changes: AuditChanges | null;
  ip_address: string | null;
  timestamp: string;
}

export interface PaginatedAuditResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: AuditLogEntry[];
}

export const auditAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedAuditResponse>('/api/audit-logs/', { params }),
};
