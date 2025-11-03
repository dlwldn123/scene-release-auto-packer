/** Wizard API service. */

import { apiRequest } from './api';

export interface WizardDraft {
  job_id?: number;
  step: number;
  step_data: Record<string, unknown>;
}

export interface Rule {
  id: number;
  name: string;
  scene?: string;
  section?: string;
  year?: number;
}

export const wizardApi = {
  /**
   * Create wizard draft (steps 1-3).
   */
  async createDraft(data: {
    group: string;
    release_type: string;
    rule_id: number;
  }) {
    return apiRequest<{ release_id: number; job_id: number; message: string }>(
      '/wizard/draft',
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Get wizard draft.
   */
  async getDraft(jobId: number) {
    return apiRequest<{ job_id: number; config: Record<string, unknown> }>(
      `/wizard/draft/${jobId}`
    );
  },

  /**
   * List available rules.
   */
  async listRules(releaseType?: string) {
    const params = releaseType ? `?release_type=${releaseType}` : '';
    return apiRequest<{ rules: Rule[] }>(`/wizard/rules${params}`);
  },
};
