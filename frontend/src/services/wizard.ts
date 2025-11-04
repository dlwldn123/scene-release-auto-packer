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

export interface FileUploadResponse {
  message: string;
  file_path: string;
  file_type: 'local' | 'remote';
  file_size?: number;
}

export interface AnalysisResponse {
  message: string;
  analysis: Record<string, unknown>;
}

export interface Template {
  id: number;
  name: string;
  description: string;
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

  /**
   * Upload file (step 4).
   */
  async uploadFile(releaseId: number, file: File | string) {
    if (typeof file === 'string') {
      // Remote URL
      return apiRequest<FileUploadResponse>(
        `/wizard/${releaseId}/upload`,
        {
          method: 'POST',
          body: JSON.stringify({ file_url: file }),
        }
      );
    }

    // Local file
    const formData = new FormData();
    formData.append('file', file);

    return apiRequest<FileUploadResponse>(
      `/wizard/${releaseId}/upload`,
      {
        method: 'POST',
        body: formData,
      }
    );
  },

  /**
   * Analyze file (step 5).
   */
  async analyzeFile(releaseId: number) {
    return apiRequest<AnalysisResponse>(
      `/wizard/${releaseId}/analyze`,
      {
        method: 'POST',
      }
    );
  },

  /**
   * Update metadata (step 6).
   */
  async updateMetadata(releaseId: number, enrichedMetadata: Record<string, unknown>) {
    return apiRequest<{ message: string; metadata: Record<string, unknown> }>(
      `/wizard/${releaseId}/metadata`,
      {
        method: 'POST',
        body: JSON.stringify({ enriched_metadata: enrichedMetadata }),
      }
    );
  },

  /**
   * List templates (step 7).
   */
  async listTemplates(releaseId: number) {
    return apiRequest<{ templates: Template[] }>(
      `/wizard/${releaseId}/templates`
    );
  },

  /**
   * Select template (step 7).
   */
  async selectTemplate(releaseId: number, templateId?: number) {
    return apiRequest<{ message: string; template_id?: number }>(
      `/wizard/${releaseId}/templates`,
      {
        method: 'POST',
        body: JSON.stringify({ template_id: templateId }),
      }
    );
  },

  /**
   * Update packaging options (step 8).
   */
  async updateOptions(releaseId: number, options: Record<string, unknown>) {
    return apiRequest<{ message: string; options: Record<string, unknown> }>(
      `/wizard/${releaseId}/options`,
      {
        method: 'POST',
        body: JSON.stringify({ options }),
      }
    );
  },

  /**
   * Finalize release (step 9).
   */
  async finalizeRelease(releaseId: number, destinationId?: number) {
    return apiRequest<{
      message: string;
      release_id: number;
      job_id?: number;
      status: string;
    }>(
      `/wizard/${releaseId}/finalize`,
      {
        method: 'POST',
        body: JSON.stringify({ destination_id: destinationId }),
      }
    );
  },
};
