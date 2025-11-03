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
   * Save wizard draft.
   */
  async saveDraft(draft: WizardDraft) {
    return apiRequest<{ job_id: number; step: number }>(
      '/wizard/draft',
      {
        method: draft.job_id ? 'PUT' : 'POST',
        body: JSON.stringify(draft),
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
