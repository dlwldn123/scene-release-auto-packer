/** Roles API service. */

import { apiRequest } from './api';

export interface Role {
  id: number;
  name: string;
  description?: string;
  permissions: Array<{ id: number; name: string }>;
  users_count: number;
  created_at: string;
}

export interface ListRolesParams {
  page?: number;
  per_page?: number;
  name?: string;
}

export interface CreateRoleData {
  name: string;
  description?: string;
  permission_ids?: number[];
}

export interface UpdateRoleData {
  name?: string;
  description?: string;
  permission_ids?: number[];
}

export const rolesApi = {
  /**
   * List roles.
   */
  async list(params: ListRolesParams = {}) {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.per_page) queryParams.append('per_page', params.per_page.toString());
    if (params.name) queryParams.append('name', params.name);

    const queryString = queryParams.toString();
    return apiRequest<{
      roles: Role[];
      pagination: {
        page: number;
        per_page: number;
        total: number;
        pages: number;
      };
    }>(`/roles${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Get role by ID.
   */
  async get(roleId: number) {
    return apiRequest<{ role: Role }>(`/roles/${roleId}`);
  },

  /**
   * Create role.
   */
  async create(data: CreateRoleData) {
    return apiRequest<{ role: Role }>('/roles', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update role.
   */
  async update(roleId: number, data: UpdateRoleData) {
    return apiRequest<{ role: Role }>(`/roles/${roleId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete role.
   */
  async delete(roleId: number) {
    return apiRequest<{ message: string }>(`/roles/${roleId}`, {
      method: 'DELETE',
    });
  },
};
