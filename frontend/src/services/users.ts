import api from './api';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  twofa_enabled: boolean;
  last_login: string | null;
  is_locked?: boolean;
}

export interface CreateUserData {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  is_active?: boolean;
  is_staff?: boolean;
}

export interface UpdateUserData {
  email?: string;
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
  is_staff?: boolean;
}

export const userManagementService = {
  /**
   * Get all users (admin only)
   */
  async getAllUsers(): Promise<User[]> {
    const response = await api.get('/api/users/', { params: { page_size: 1000 } });
    // Handle paginated response if present
    if (response.data && typeof response.data === 'object' && 'results' in response.data) {
      return response.data.results;
    }
    return response.data;
  },

  /**
   * Get a specific user by ID (admin only)
   */
  async getUser(id: number): Promise<User> {
    const response = await api.get(`/api/users/${id}/`);
    return response.data;
  },

  /**
   * Create a new user (admin only)
   */
  async createUser(data: CreateUserData): Promise<User> {
    const response = await api.post('/api/users/', data);
    return response.data;
  },

  /**
   * Update a user (admin only)
   */
  async updateUser(id: number, data: UpdateUserData): Promise<User> {
    const response = await api.patch(`/api/users/${id}/`, data);
    return response.data;
  },

  /**
   * Delete a user (admin only)
   */
  async deleteUser(id: number): Promise<void> {
    await api.delete(`/api/users/${id}/`);
  },

  /**
   * Set a new password for a user (admin account recovery)
   */
  async resetPassword(id: number, password: string): Promise<void> {
    await api.post(`/api/users/${id}/reset-password/`, { password });
  },

  /**
   * Clear a user's 2FA enrolment so they can set it up again at next login
   */
  async resetTwoFactor(id: number): Promise<void> {
    await api.post(`/api/users/${id}/reset-2fa/`);
  },

  /**
   * Clear a lockout caused by failed login attempts
   */
  async unlock(id: number): Promise<void> {
    await api.post(`/api/users/${id}/unlock/`);
  },
};

export default userManagementService;
