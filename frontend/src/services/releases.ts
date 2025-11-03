/** Releases API service. */

import { apiRequest } from './api';

export interface Release {
  id: number;
  user_id: number;
  group_id?: number;
  release_type: string;
  status: string;
  created_at: string;
}

export interface ListReleasesParams {
  page?: number;
  per_page?: number;
  release_type?: string;
  status?: string;
  user_id?: number;
}

export const releasesApi = {
  /**
   * List releases.
   */
  async list(params: ListReleasesParams = {}) {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.per_page) queryParams.append('per_page', params.per_page.toString());
    if (params.release_type) queryParams.append('release_type', params.release_type);
    if (params.status) queryParams.append('status', params.status);
    if (params.user_id) queryParams.append('user_id', params.user_id.toString());

    const queryString = queryParams.toString();
    return apiRequest<{
      releases: Release[];
      pagination: {
        page: number;
        per_page: number;
        total: number;
        pages: number;
      };
    }>(`/releases${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Get release by ID.
   */
  async get(releaseId: number) {
    return apiRequest<{ release: Release }>(`/releases/${releaseId}`);
  },

  /**
   * Delete release.
   */
  async delete(releaseId: number) {
    return apiRequest<{ message: string }>(`/releases/${releaseId}`, {
      method: 'DELETE',
    });
  },
};
