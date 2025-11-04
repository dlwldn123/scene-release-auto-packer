/** Dashboard page component. */

import { useEffect, useState } from 'react';
// Bootstrap Icons via CSS classes
import { PageLayout } from '../components/PageLayout';
import { dashboardApi } from '../services/api';

interface DashboardStats {
  total_releases: number;
  total_jobs: number;
  user_releases: number;
  user_jobs: number;
  user: {
    id: number;
    username: string;
    email: string;
    active: boolean;
  };
}

/**
 * Dashboard page component.
 */
export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await dashboardApi.getStats();
        setStats(response || null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to load dashboard stats'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <PageLayout title="Dashboard">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout title="Dashboard">
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Dashboard" description="Vue d'ensemble de l'application">
      <div className="row g-4">
        <div className="col-md-3">
          <div className="card border rounded-lg shadow-sm">
            <div className="card-body d-flex align-items-center gap-3">
              <i
                className="bi bi-file-earmark text-primary"
                style={{ fontSize: '2rem', width: '2rem', height: '2rem' }}
                aria-hidden="true"
              />
              <div>
                <h6 className="card-title mb-0 text-muted">Total Releases</h6>
                <p className="card-text display-4 mb-0 fw-bold">
                  {stats?.total_releases || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card border rounded-lg shadow-sm">
            <div className="card-body d-flex align-items-center gap-3">
              <i
                className="bi bi-list-task text-primary"
                style={{ fontSize: '2rem', width: '2rem', height: '2rem' }}
                aria-hidden="true"
              />
              <div>
                <h6 className="card-title mb-0 text-muted">Total Jobs</h6>
                <p className="card-text display-4 mb-0 fw-bold">
                  {stats?.total_jobs || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card border rounded-lg shadow-sm">
            <div className="card-body d-flex align-items-center gap-3">
              <i
                className="bi bi-file-earmark text-success"
                style={{ fontSize: '2rem', width: '2rem', height: '2rem' }}
                aria-hidden="true"
              />
              <div>
                <h6 className="card-title mb-0 text-muted">Mes Releases</h6>
                <p className="card-text display-4 mb-0 fw-bold">
                  {stats?.user_releases || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card border rounded-lg shadow-sm">
            <div className="card-body d-flex align-items-center gap-3">
              <i
                className="bi bi-list-task text-success"
                style={{ fontSize: '2rem', width: '2rem', height: '2rem' }}
                aria-hidden="true"
              />
              <div>
                <h6 className="card-title mb-0 text-muted">Mes Jobs</h6>
                <p className="card-text display-4 mb-0 fw-bold">
                  {stats?.user_jobs || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {stats?.user && (
        <div className="row mt-4">
          <div className="col-12">
            <div className="card border rounded-lg shadow-sm">
              <div className="card-body">
                <div className="d-flex align-items-center gap-3 mb-3">
                  <i
                    className="bi bi-person text-primary"
                    style={{ fontSize: '2rem', width: '2rem', height: '2rem' }}
                    aria-hidden="true"
                  />
                  <h5 className="card-title mb-0">Informations utilisateur</h5>
                </div>
                <p className="card-text mb-2">
                  <strong>Username:</strong> {stats.user.username}
                </p>
                <p className="card-text mb-0">
                  <strong>Email:</strong> {stats.user.email}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </PageLayout>
  );
}
