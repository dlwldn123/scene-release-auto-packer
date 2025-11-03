/** Configurations API service. */

import { apiRequest } from './api';

export interface Configuration {
  id: number;
  key: string;
  value: string;
  category?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface ListConfigurationsParams {
  page?: number;
  per_page?: number;
  category?: string;
  key?: string;
}

export interface CreateConfigurationData {
  key: string;
  value: string;
  category?: string;
  description?: string;
}

export interface UpdateConfigurationData {
  key?: string;
  value?: string;
  category?: string;
  description?: string;
}

export const configurationsApi = {
  /**
   * List configurations.
   */
  async list(params: ListConfigurationsParams = {}) {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.per_page) queryParams.append('per_page', params.per_page.toString());
    if (params.category) queryParams.append('category', params.category);
    if (params.key) queryParams.append('key', params.key);

    const queryString = queryParams.toString();
    return apiRequest<{
      configurations: Configuration[];
      pagination: {
        page: number;
        per_page: number;
        total: number;
        pages: number;
      };
    }>(`/config${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Get configuration by ID.
   */
  async get(configId: number) {
    return apiRequest<{ configuration: Configuration }>(`/config/${configId}`);
  },

  /**
   * Get configuration by key.
   */
  async getByKey(key: string) {
    return apiRequest<{ configuration: Configuration }>(`/config/key/${key}`);
  },

  /**
   * Create configuration.
   */
  async create(data: CreateConfigurationData) {
    return apiRequest<{ configuration: Configuration }>('/config', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update configuration.
   */
  async update(configId: number, data: UpdateConfigurationData) {
    return apiRequest<{ configuration: Configuration }>(`/config/${configId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete configuration.
   */
  async delete(configId: number) {
    return apiRequest<{ message: string }>(`/config/${configId}`, {
      method: 'DELETE',
    });
  },
};
