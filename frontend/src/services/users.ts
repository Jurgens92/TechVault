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
    const response = await api.get('/api/users/');
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
};

export default userManagementService;
