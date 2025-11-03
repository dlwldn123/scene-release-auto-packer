/** Users API service. */

import { apiRequest } from './api';

export interface User {
  id: number;
  username: string;
  email: string;
  active: boolean;
  note?: string;
  roles: Array<{ id: number; name: string }>;
  groups: Array<{ id: number; name: string }>;
  created_at: string;
  modify_at?: string;
}

export interface ListUsersParams {
  page?: number;
  per_page?: number;
  username?: string;
  email?: string;
  role_id?: number;
}

export interface CreateUserData {
  username: string;
  email: string;
  password: string;
}

export interface UpdateUserData {
  username?: string;
  email?: string;
  password?: string;
  role_ids?: number[];
}

export const usersApi = {
  /**
   * List users.
   */
  async list(params: ListUsersParams = {}) {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.per_page) queryParams.append('per_page', params.per_page.toString());
    if (params.username) queryParams.append('username', params.username);
    if (params.email) queryParams.append('email', params.email);
    if (params.role_id) queryParams.append('role_id', params.role_id.toString());

    const queryString = queryParams.toString();
    return apiRequest<{
      users: User[];
      pagination: {
        page: number;
        per_page: number;
        total: number;
        pages: number;
      };
    }>(`/users${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Get user by ID.
   */
  async get(userId: number) {
    return apiRequest<{ user: User }>(`/users/${userId}`);
  },

  /**
   * Create user.
   */
  async create(data: CreateUserData) {
    return apiRequest<{ user: User }>('/users', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update user.
   */
  async update(userId: number, data: UpdateUserData) {
    return apiRequest<{ user: User }>(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete user.
   */
  async delete(userId: number) {
    return apiRequest<{ message: string }>(`/users/${userId}`, {
      method: 'DELETE',
    });
  },
};
