import api from './api';

export interface HealthCheck {
  status: 'healthy' | 'warning' | 'unhealthy';
  [key: string]: unknown;
}

export interface DatabaseHealth extends HealthCheck {
  engine?: string;
  name?: string;
  error?: string;
}

export interface VersionsHealth extends HealthCheck {
  django?: string;
  python?: string;
  environment?: string;
  debug_mode?: boolean;
}

export interface UsersHealth extends HealthCheck {
  total?: number;
  active?: number;
  inactive?: number;
  admins?: number;
  locked_accounts?: number;
  twofa_enabled?: number;
  twofa_disabled?: number;
  twofa_percentage?: number;
  recent_logins_24h?: number;
  recent_logins_7d?: number;
  never_logged_in?: number;
  error?: string;
}

export interface DataHealth extends HealthCheck {
  active_records?: Record<string, number>;
  deleted_records?: Record<string, number>;
  total_active?: number;
  total_deleted?: number;
  error?: string;
}

export interface SecurityHealth extends HealthCheck {
  https_enforced?: boolean;
  hsts_enabled?: boolean;
  csrf_protection?: boolean;
  session_cookie_secure?: boolean;
  rate_limiting?: boolean;
}

export interface StorageHealth extends HealthCheck {
  type?: string;
  database_size_mb?: number;
  message?: string;
  error?: string;
}

export interface DiskSpaceHealth extends HealthCheck {
  path?: string;
  total_gb?: number;
  used_gb?: number;
  free_gb?: number;
  used_percent?: number;
  free_percent?: number;
  error?: string;
}

export interface SystemHealthResponse {
  status: 'healthy' | 'warning' | 'unhealthy';
  timestamp: string;
  checks: {
    database?: DatabaseHealth;
    versions?: VersionsHealth;
    users?: UsersHealth;
    data?: DataHealth;
    security?: SecurityHealth;
    storage?: StorageHealth;
    disk_space?: DiskSpaceHealth;
  };
}

export const doctorService = {
  /**
   * Get system health status (admin only)
   */
  async getSystemHealth(): Promise<SystemHealthResponse> {
    const response = await api.get('/api/admin/health/');
    return response.data;
  },
};

export default doctorService;
