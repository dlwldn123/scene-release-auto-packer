/** Permissions API service. */

import { apiRequest } from './api';

export interface Permission {
  id: number;
  resource: string;
  action: string;
  created_at?: string;
}

export interface ListPermissionsParams {
  resource?: string;
  action?: string;
}

export const permissionsApi = {
  /**
   * List permissions.
   */
  async list(params: ListPermissionsParams = {}) {
    const queryParams = new URLSearchParams();
    if (params.resource) queryParams.append('resource', params.resource);
    if (params.action) queryParams.append('action', params.action);

    const queryString = queryParams.toString();
    return apiRequest<{
      permissions: Permission[];
    }>(`/permissions${queryString ? `?${queryString}` : ''}`);
  },
};
