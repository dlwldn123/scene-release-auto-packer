/** Wizard Step 8: Packaging options configuration. */

import { useState } from 'react';

interface StepOptionsProps {
  onNext: (data: { options: Record<string, unknown> }) => void;
}

/**
 * Step 8: Packaging options component.
 */
export function StepOptions({ onNext }: StepOptionsProps) {
  const [options, setOptions] = useState<Record<string, unknown>>({
    create_nfo: true,
    create_sample: false,
    create_sfv: false,
    create_md5: false,
    compress_type: 'zip',
    include_metadata: true,
  });

  const handleChange = (field: string, value: unknown) => {
    setOptions(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext({ options });
  };

  return (
    <div className="wizard-step">
      <h3>Étape 8 : Options Packaging</h3>
      <p className="text-muted">
        Configurez les options de packaging pour la release.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="card mb-3">
          <div className="card-header">Fichiers à inclure</div>
          <div className="card-body">
            <div className="mb-3">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="create_nfo"
                  checked={Boolean(options.create_nfo)}
                  onChange={(e) => handleChange('create_nfo', e.target.checked)}
                />
                <label className="form-check-label" htmlFor="create_nfo">
                  Créer fichier NFO
                </label>
              </div>
            </div>

            <div className="mb-3">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="create_sample"
                  checked={Boolean(options.create_sample)}
                  onChange={(e) => handleChange('create_sample', e.target.checked)}
                />
                <label className="form-check-label" htmlFor="create_sample">
                  Créer échantillon (sample)
                </label>
              </div>
            </div>

            <div className="mb-3">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="create_sfv"
                  checked={Boolean(options.create_sfv)}
                  onChange={(e) => handleChange('create_sfv', e.target.checked)}
                />
                <label className="form-check-label" htmlFor="create_sfv">
                  Créer fichier SFV (checksums)
                </label>
              </div>
            </div>

            <div className="mb-3">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="create_md5"
                  checked={Boolean(options.create_md5)}
                  onChange={(e) => handleChange('create_md5', e.target.checked)}
                />
                <label className="form-check-label" htmlFor="create_md5">
                  Créer fichier MD5
                </label>
              </div>
            </div>

            <div className="mb-3">
              <div className="form-check">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="include_metadata"
                  checked={Boolean(options.include_metadata)}
                  onChange={(e) => handleChange('include_metadata', e.target.checked)}
                />
                <label className="form-check-label" htmlFor="include_metadata">
                  Inclure métadonnées
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className="mb-3">
          <label htmlFor="compress_type" className="form-label">
            Type de compression
          </label>
          <select
            className="form-select"
            id="compress_type"
            value={String(options.compress_type || 'zip')}
            onChange={(e) => handleChange('compress_type', e.target.value)}
          >
            <option value="zip">ZIP</option>
            <option value="rar">RAR</option>
            <option value="7z">7Z</option>
            <option value="none">Aucune compression</option>
          </select>
          <div className="form-text">
            Format d'archive pour le package final
          </div>
        </div>

        <div className="alert alert-info" role="alert">
          Les options peuvent être modifiées ultérieurement dans les paramètres de release.
        </div>

        <div className="d-flex justify-content-end gap-2 mt-3">
          <button
            type="submit"
            className="btn btn-primary"
          >
            Suivant
          </button>
        </div>
      </form>
    </div>
  );
}
