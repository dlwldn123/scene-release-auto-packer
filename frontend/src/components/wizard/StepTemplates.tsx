/** Wizard Step 7: NFO templates selection with preview. */

import { useState, useEffect } from 'react';
import { wizardApi, Template } from '../../services/wizard';
import { NFOViewer } from '../NFOViewer';

interface StepTemplatesProps {
  releaseId?: number;
  onNext: (data: { template_id?: number }) => void;
}

/**
 * Step 7: NFO templates selection component with preview.
 */
export function StepTemplates({ releaseId, onNext }: StepTemplatesProps) {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | undefined>();
  const [preview, setPreview] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (releaseId) {
      loadTemplates();
    }
  }, [releaseId]);

  const loadTemplates = async () => {
    if (!releaseId) return;

    setLoading(true);
    setError(null);
    try {
      const response = await wizardApi.listTemplates(releaseId);
      setTemplates(response.templates || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Échec du chargement des templates');
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateSelect = async (templateId: number) => {
    setSelectedTemplateId(templateId);
    // In a real implementation, fetch preview from backend
    setPreview(`Template ${templateId} preview\n\nExample NFO content...`);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!releaseId) {
      setError('Release ID manquant');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await wizardApi.selectTemplate(releaseId, selectedTemplateId);
      onNext({ template_id: selectedTemplateId });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Échec de la sélection du template');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="wizard-step">
      <h3>Étape 7 : Templates NFO</h3>
      <p className="text-muted">
        Sélectionnez un template NFO ou utilisez le template par défaut.
      </p>

      {loading && !templates.length ? (
        <div className="text-center py-4">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Chargement...</span>
          </div>
        </div>
      ) : error ? (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      ) : (
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Sélectionner un template</label>
            {templates.length === 0 ? (
              <div className="alert alert-info" role="alert">
                Aucun template disponible. Le template par défaut sera utilisé.
              </div>
            ) : (
              <div className="list-group">
                {templates.map((template) => (
                  <label
                    key={template.id}
                    className={`list-group-item list-group-item-action ${
                      selectedTemplateId === template.id ? 'active' : ''
                    }`}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="form-check">
                      <input
                        className="form-check-input"
                        type="radio"
                        name="template"
                        id={`template-${template.id}`}
                        checked={selectedTemplateId === template.id}
                        onChange={() => handleTemplateSelect(template.id)}
                      />
                      <label
                        className="form-check-label w-100"
                        htmlFor={`template-${template.id}`}
                      >
                        <strong>{template.name}</strong>
                        {template.description && (
                          <div className="small text-muted">{template.description}</div>
                        )}
                      </label>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          {preview && (
            <div className="mb-3">
              <label className="form-label">Aperçu</label>
              <div className="border rounded p-3 bg-light">
                <NFOViewer content={preview} maxWidth={80} />
              </div>
            </div>
          )}

          <div className="alert alert-info" role="alert">
            Si aucun template n'est sélectionné, le template par défaut sera utilisé.
          </div>

          <div className="d-flex justify-content-end gap-2 mt-3">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                  Enregistrement...
                </>
              ) : (
                'Suivant'
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
