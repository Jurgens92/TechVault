import api from './api';
import { LoginCredentials, RegisterData, User, LoginResponse } from '@/types/auth';

export const authService = {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await api.post('/api/auth/login/', credentials);

    // Check if 2FA is required
    if (response.data.requires_2fa) {
      return {
        requires_2fa: true,
        email: response.data.email,
        message: response.data.message,
      };
    }

    // The server sets the session as HttpOnly cookies; tokens in the response body
    // are intentionally ignored so they are never held by JavaScript.
    return {
      user: response.data.user,
      backup_code_used: response.data.backup_code_used,
      remaining_backup_codes: response.data.remaining_backup_codes,
      warning: response.data.warning,
      requires_2fa_setup: response.data.requires_2fa_setup,
    };
  },

  async register(data: RegisterData): Promise<{ user: User }> {
    const response = await api.post('/api/auth/registration/', data);
    return { user: response.data.user };
  },

  async logout(): Promise<void> {
    try {
      await api.post('/api/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  },

  async getCurrentUser(options: { silent?: boolean } = {}): Promise<User> {
    // silent: used on app start, where "not signed in" is an expected answer and
    // must not bounce the user to the login page.
    const response = await api.get('/api/user/profile/', {
      skipAuthRedirect: options.silent,
    } as any);
    return response.data;
  },

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await api.post('/api/auth/password/change/', {
      old_password: oldPassword,
      new_password1: newPassword,
      new_password2: newPassword,
    });
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.patch('/api/user/profile/', data);
    return response.data;
  },
};

export default authService;
