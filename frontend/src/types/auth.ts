export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  twofa_enabled?: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
  twofa_token?: string;
}

export interface RegisterData {
  email: string;
  password1: string;
  password2: string;
  first_name: string;
  last_name: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface LoginResponse {
  requires_2fa?: boolean;
  email?: string;
  message?: string;
  user?: User;
  tokens?: AuthTokens;
  backup_code_used?: boolean;
  remaining_backup_codes?: number;
  warning?: string;
  requires_2fa_setup?: boolean;
}

export interface ApiError {
  response?: {
    data?: {
      error?: string;
      message?: string;
      detail?: string;
    };
    status?: number;
  };
  message?: string;
}
