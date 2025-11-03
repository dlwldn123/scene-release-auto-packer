/** Release actions component for special actions. */

import { useState } from 'react';
import type { ActionResponse } from '../services/releases';
import { releasesApi } from '../services/releases';

interface ReleaseActionsProps {
  releaseId: number;
  onActionComplete?: () => void;
}

/**
 * Release actions component for special actions (NFOFIX, READNFO, REPACK, DIRFIX).
 */
export function ReleaseActions({
  releaseId,
  onActionComplete,
}: ReleaseActionsProps) {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleAction = async (
    action: 'nfofix' | 'readnfo' | 'repack' | 'dirfix',
    options?: Record<string, unknown>
  ) => {
    try {
      setLoading(action);
      setError(null);
      setSuccess(null);

      let response: { data?: ActionResponse };
      switch (action) {
        case 'nfofix':
          response = await releasesApi.nfofix(releaseId);
          break;
        case 'readnfo':
          response = await releasesApi.readnfo(releaseId);
          break;
        case 'repack':
          response = await releasesApi.repack(releaseId, options);
          break;
        case 'dirfix':
          response = await releasesApi.dirfix(releaseId);
          break;
      }

      setSuccess(response.data?.message || 'Action réussie');
      if (onActionComplete) {
        onActionComplete();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de l'action");
    } finally {
      setLoading(null);
    }
  };

  const handleRepack = () => {
    const zipSize = prompt('Nouvelle taille ZIP (MB):', '50');
    if (zipSize) {
      handleAction('repack', { zip_size: parseInt(zipSize, 10) });
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h5 className="mb-0">Actions Spéciales</h5>
      </div>
      <div className="card-body">
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success" role="alert">
            {success}
          </div>
        )}

        <div className="d-grid gap-2 d-md-block">
          <button
            type="button"
            className="btn btn-outline-primary"
            onClick={() => handleAction('nfofix')}
            disabled={loading !== null}
            aria-label="Corriger le fichier NFO"
          >
            {loading === 'nfofix' ? (
              <>
                <span
                  className="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                />
                Traitement...
              </>
            ) : (
              <>
                <i className="bi bi-file-earmark-text" aria-hidden="true" />{' '}
                NFOFIX
              </>
            )}
          </button>

          <button
            type="button"
            className="btn btn-outline-primary"
            onClick={() => handleAction('readnfo')}
            disabled={loading !== null}
            aria-label="Lire NFO et régénérer"
          >
            {loading === 'readnfo' ? (
              <>
                <span
                  className="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                />
                Traitement...
              </>
            ) : (
              <>
                <i
                  className="bi bi-file-earmark-arrow-down"
                  aria-hidden="true"
                />{' '}
                READNFO
              </>
            )}
          </button>

          <button
            type="button"
            className="btn btn-outline-primary"
            onClick={handleRepack}
            disabled={loading !== null}
            aria-label="Repackager la release"
          >
            {loading === 'repack' ? (
              <>
                <span
                  className="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                />
                Traitement...
              </>
            ) : (
              <>
                <i className="bi bi-archive" aria-hidden="true" /> REPACK
              </>
            )}
          </button>

          <button
            type="button"
            className="btn btn-outline-primary"
            onClick={() => handleAction('dirfix')}
            disabled={loading !== null}
            aria-label="Corriger la structure de répertoires"
          >
            {loading === 'dirfix' ? (
              <>
                <span
                  className="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                />
                Traitement...
              </>
            ) : (
              <>
                <i className="bi bi-folder-symlink" aria-hidden="true" /> DIRFIX
              </>
            )}
          </button>
        </div>

        <div className="mt-3">
          <small className="text-muted">
            Ces actions créent des jobs asynchrones. Consultez l'onglet Jobs
            pour suivre leur progression.
          </small>
        </div>
      </div>
    </div>
  );
}
