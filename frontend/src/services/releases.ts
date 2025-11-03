/** Releases API service. */

import { apiRequest } from './api';

export interface Release {
  id: number;
  user_id: number;
  group_id?: number;
  release_type: string;
  status: string;
  release_metadata?: Record<string, unknown>;
  config?: Record<string, unknown>;
  file_path?: string;
  created_at: string;
}

export interface ReleaseListParams {
  page?: number;
  per_page?: number;
  release_type?: string;
  status?: string;
  user_id?: number;
  group_id?: number;
  search?: string;
  sort?: string;
  sort_by?: string;
  order?: 'asc' | 'desc';
  sort_order?: 'asc' | 'desc';
}

export interface ReleaseListResponse {
  releases: Release[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface ActionResponse {
  message: string;
  job_id: number;
}

export const releasesApi = {
  /**
   * List releases with filters and pagination.
   */
  async list(params: ReleaseListParams = {}) {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.per_page)
      queryParams.append('per_page', params.per_page.toString());
    if (params.release_type)
      queryParams.append('release_type', params.release_type);
    if (params.status) queryParams.append('status', params.status);
    if (params.user_id)
      queryParams.append('user_id', params.user_id.toString());
    if (params.group_id)
      queryParams.append('group_id', params.group_id.toString());
    if (params.search) queryParams.append('search', params.search);
    if (params.sort_by) queryParams.append('sort_by', params.sort_by);
    if (params.sort_order) queryParams.append('sort_order', params.sort_order);
    // Legacy support
    if (params.sort && !params.sort_by)
      queryParams.append('sort_by', params.sort);
    if (params.order && !params.sort_order)
      queryParams.append('sort_order', params.order);

    return apiRequest<ReleaseListResponse>(
      `/releases?${queryParams.toString()}`
    );
  },

  /**
   * Get release by ID.
   */
  async get(releaseId: number) {
    return apiRequest<{ release: Release }>(`/releases/${releaseId}`);
  },

  /**
   * Update release.
   */
  async update(releaseId: number, data: Partial<Release>) {
    return apiRequest<{ release: Release; message: string }>(
      `/releases/${releaseId}`,
      {
        method: 'PUT',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Delete release.
   */
  async delete(releaseId: number) {
    return apiRequest<{ message: string }>(`/releases/${releaseId}`, {
      method: 'DELETE',
    });
  },

  /**
   * NFOFIX action - Fix NFO file.
   */
  async nfofix(releaseId: number) {
    return apiRequest<ActionResponse>(`/releases/${releaseId}/actions/nfofix`, {
      method: 'POST',
    });
  },

  /**
   * READNFO action - Read NFO and regenerate structure.
   */
  async readnfo(releaseId: number) {
    return apiRequest<ActionResponse>(
      `/releases/${releaseId}/actions/readnfo`,
      {
        method: 'POST',
      }
    );
  },

  /**
   * REPACK action - Repack release with new options.
   */
  async repack(releaseId: number, options?: Record<string, unknown>) {
    return apiRequest<ActionResponse>(`/releases/${releaseId}/actions/repack`, {
      method: 'POST',
      body: options ? JSON.stringify(options) : undefined,
    });
  },

  /**
   * DIRFIX action - Fix directory structure.
   */
  async dirfix(releaseId: number) {
    return apiRequest<ActionResponse>(`/releases/${releaseId}/actions/dirfix`, {
      method: 'POST',
    });
  },
};
