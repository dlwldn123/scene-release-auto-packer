/** Release edit page component. */

import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { PageLayout } from '../components/PageLayout';
import type { Release } from '../services/releases';
import { releasesApi } from '../services/releases';

/**
 * Release edit page component.
 */
export function ReleaseEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [release, setRelease] = useState<Release | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<{
    release_metadata?: Record<string, unknown>;
    config?: Record<string, unknown>;
    status?: string;
  }>({});

  useEffect(() => {
    const fetchRelease = async () => {
      if (!id) {
        setError('ID de release manquant');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await releasesApi.get(parseInt(id, 10));
        const releaseData = response.data?.release;
        if (releaseData) {
          setRelease(releaseData);
          setFormData({
            release_metadata: releaseData.release_metadata || {},
            config: releaseData.config || {},
            status: releaseData.status,
          });
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Erreur lors du chargement'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchRelease();
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !release) {
      return;
    }

    try {
      setSaving(true);
      await releasesApi.update(parseInt(id, 10), formData);
      navigate(`/releases/${id}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Erreur lors de la sauvegarde'
      );
    } finally {
      setSaving(false);
    }
  };

  const handleMetadataChange = (key: string, value: unknown) => {
    setFormData(prev => ({
      ...prev,
      release_metadata: {
        ...(prev.release_metadata || {}),
        [key]: value,
      },
    }));
  };

  if (loading) {
    return (
      <PageLayout title="Édition Release" description="Chargement...">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Chargement...</span>
          </div>
        </div>
      </PageLayout>
    );
  }

  if (error || !release) {
    return (
      <PageLayout title="Erreur" description={error || 'Release non trouvée'}>
        <div className="alert alert-danger" role="alert">
          {error || 'Release non trouvée'}
        </div>
        <Link to="/releases" className="btn btn-primary">
          Retour à la liste
        </Link>
      </PageLayout>
    );
  }

  const metadata = formData.release_metadata || {};
  const commonKeys = ['title', 'author', 'year', 'isbn', 'language'];

  return (
    <PageLayout
      title={`Éditer Release #${release.id}`}
      description={`Modifier les informations de la release ${release.id}`}
    >
      <div className="mb-3">
        <Link
          to={`/releases/${release.id}`}
          className="btn btn-outline-secondary"
        >
          <i className="bi bi-arrow-left" aria-hidden="true" /> Annuler
        </Link>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="row">
          <div className="col-md-6">
            <div className="card mb-3">
              <div className="card-header">
                <h5 className="mb-0">Métadonnées</h5>
              </div>
              <div className="card-body">
                {commonKeys.map(key => (
                  <div key={key} className="mb-3">
                    <label htmlFor={`metadata-${key}`} className="form-label">
                      {key.charAt(0).toUpperCase() + key.slice(1)}
                    </label>
                    <input
                      id={`metadata-${key}`}
                      type="text"
                      className="form-control"
                      value={String(metadata[key] || '')}
                      onChange={e => handleMetadataChange(key, e.target.value)}
                    />
                  </div>
                ))}

                <div className="mb-3">
                  <label htmlFor="metadata-other" className="form-label">
                    Autres métadonnées (JSON)
                  </label>
                  <textarea
                    id="metadata-other"
                    className="form-control font-monospace"
                    rows={5}
                    value={JSON.stringify(metadata, null, 2)}
                    onChange={e => {
                      try {
                        const parsed = JSON.parse(e.target.value);
                        setFormData(prev => ({
                          ...prev,
                          release_metadata: parsed,
                        }));
                      } catch {
                        // Invalid JSON, ignore
                      }
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <div className="card mb-3">
              <div className="card-header">
                <h5 className="mb-0">Configuration</h5>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <label htmlFor="status" className="form-label">
                    Statut
                  </label>
                  <select
                    id="status"
                    className="form-select"
                    value={formData.status || 'draft'}
                    onChange={e =>
                      setFormData(prev => ({ ...prev, status: e.target.value }))
                    }
                  >
                    <option value="draft">Brouillon</option>
                    <option value="processing">En traitement</option>
                    <option value="completed">Complété</option>
                    <option value="failed">Échoué</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label htmlFor="config" className="form-label">
                    Configuration (JSON)
                  </label>
                  <textarea
                    id="config"
                    className="form-control font-monospace"
                    rows={10}
                    value={JSON.stringify(formData.config || {}, null, 2)}
                    onChange={e => {
                      try {
                        const parsed = JSON.parse(e.target.value);
                        setFormData(prev => ({ ...prev, config: parsed }));
                      } catch {
                        // Invalid JSON, ignore
                      }
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="d-flex gap-2">
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? (
              <>
                <span
                  className="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                />
                Sauvegarde...
              </>
            ) : (
              <>
                <i className="bi bi-check-circle" aria-hidden="true" />{' '}
                Sauvegarder
              </>
            )}
          </button>
          <Link to={`/releases/${release.id}`} className="btn btn-secondary">
            Annuler
          </Link>
        </div>
      </form>
    </PageLayout>
  );
}
