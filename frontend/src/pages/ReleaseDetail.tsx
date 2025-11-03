/** Release detail page component. */

import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { PageLayout } from '../components/PageLayout';
import { ReleaseActions } from '../components/ReleaseActions';
import type { Release } from '../services/releases';
import { releasesApi } from '../services/releases';

/**
 * Release detail page component.
 */
export function ReleaseDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [release, setRelease] = useState<Release | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
        setRelease(response.data?.release || null);
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

  const handleDelete = async () => {
    if (
      !release ||
      !confirm('Êtes-vous sûr de vouloir supprimer cette release ?')
    ) {
      return;
    }

    try {
      await releasesApi.delete(release.id);
      navigate('/releases');
    } catch {
      alert('Erreur lors de la suppression');
    }
  };

  if (loading) {
    return (
      <PageLayout title="Détail Release" description="Chargement...">
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

  const metadata = (release.release_metadata as Record<string, unknown>) || {};
  const config = (release.config as Record<string, unknown>) || {};

  return (
    <PageLayout
      title={`Release #${release.id}`}
      description={`Détails de la release ${release.id}`}
    >
      <div className="mb-3">
        <Link to="/releases" className="btn btn-outline-secondary">
          <i className="bi bi-arrow-left" aria-hidden="true" /> Retour à la
          liste
        </Link>
        <Link
          to={`/releases/${release.id}/edit`}
          className="btn btn-primary ms-2"
          aria-label="Éditer cette release"
        >
          <i className="bi bi-pencil" aria-hidden="true" /> Éditer
        </Link>
        <button
          className="btn btn-danger ms-2"
          onClick={handleDelete}
          aria-label="Supprimer cette release"
        >
          <i className="bi bi-trash" aria-hidden="true" /> Supprimer
        </button>
      </div>

      <div className="row">
        <div className="col-md-6">
          <div className="card mb-3">
            <div className="card-header">
              <h5 className="mb-0">Informations Générales</h5>
            </div>
            <div className="card-body">
              <dl className="row mb-0">
                <dt className="col-sm-4">ID</dt>
                <dd className="col-sm-8">{release.id}</dd>

                <dt className="col-sm-4">Type</dt>
                <dd className="col-sm-8">
                  <span className="badge bg-primary">
                    {release.release_type}
                  </span>
                </dd>

                <dt className="col-sm-4">Statut</dt>
                <dd className="col-sm-8">
                  <span
                    className={`badge bg-${
                      release.status === 'completed'
                        ? 'success'
                        : release.status === 'draft'
                          ? 'warning'
                          : 'secondary'
                    }`}
                  >
                    {release.status}
                  </span>
                </dd>

                <dt className="col-sm-4">Créé le</dt>
                <dd className="col-sm-8">
                  {new Date(release.created_at).toLocaleString('fr-FR')}
                </dd>

                {release.group_id && (
                  <>
                    <dt className="col-sm-4">Groupe ID</dt>
                    <dd className="col-sm-8">{release.group_id}</dd>
                  </>
                )}

                {release.file_path && (
                  <>
                    <dt className="col-sm-4">Chemin fichier</dt>
                    <dd className="col-sm-8">
                      <code>{release.file_path}</code>
                    </dd>
                  </>
                )}
              </dl>
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card mb-3">
            <div className="card-header">
              <h5 className="mb-0">Métadonnées</h5>
            </div>
            <div className="card-body">
              {Object.keys(metadata).length > 0 ? (
                <dl className="row mb-0">
                  {Object.entries(metadata).map(([key, value]) => (
                    <div key={key}>
                      <dt className="col-sm-12">{key}</dt>
                      <dd className="col-sm-12">
                        {typeof value === 'object' ? (
                          <pre className="mb-0">
                            {JSON.stringify(value, null, 2)}
                          </pre>
                        ) : (
                          String(value)
                        )}
                      </dd>
                    </div>
                  ))}
                </dl>
              ) : (
                <p className="text-muted mb-0">Aucune métadonnée</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {Object.keys(config).length > 0 && (
        <div className="card mb-3">
          <div className="card-header">
            <h5 className="mb-0">Configuration</h5>
          </div>
          <div className="card-body">
            <pre className="mb-0">{JSON.stringify(config, null, 2)}</pre>
          </div>
        </div>
      )}

      <ReleaseActions
        releaseId={release.id}
        onActionComplete={() => {
          // Refresh release data after action
          const fetchRelease = async () => {
            try {
              const response = await releasesApi.get(release.id);
              if (response.data?.release) {
                setRelease(response.data.release);
              }
            } catch {
              // Ignore errors
            }
          };
          fetchRelease();
        }}
      />
    </PageLayout>
  );
}
