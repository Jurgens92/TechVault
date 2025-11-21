import api, { setTokens, clearTokens } from './api';
import { LoginCredentials, RegisterData, User } from '@/types/auth';

export const authService = {
  async login(credentials: LoginCredentials): Promise<{ user: User; tokens: { access: string; refresh: string } }> {
    const response = await api.post('/api/auth/login/', credentials);
    const { access_token, refresh_token, user } = response.data;

    setTokens({ access: access_token, refresh: refresh_token });

    return {
      user,
      tokens: {
        access: access_token,
        refresh: refresh_token,
      },
    };
  },

  async register(data: RegisterData): Promise<{ user: User; tokens: { access: string; refresh: string } }> {
    const response = await api.post('/api/auth/registration/', data);
    const { access_token, refresh_token, user } = response.data;

    setTokens({ access: access_token, refresh: refresh_token });

    return {
      user,
      tokens: {
        access: access_token,
        refresh: refresh_token,
      },
    };
  },

  async logout(): Promise<void> {
    try {
      await api.post('/api/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearTokens();
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/api/user/profile/');
    return response.data;
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.patch('/api/user/profile/', data);
    return response.data;
  },
};

export default authService;
