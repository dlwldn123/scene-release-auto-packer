/** Wizard Step 9: Destination selection for finalization. */

import { useState } from 'react';

interface StepDestinationProps {
  onFinalize: (data: { destination_id?: number }) => void;
}

interface Destination {
  id: number;
  name: string;
  type: 'ftp' | 'ssh';
  host: string;
}

/**
 * Step 9: Destination selection component for finalization.
 */
export function StepDestination({ onFinalize }: StepDestinationProps) {
  const [selectedDestinationId, setSelectedDestinationId] = useState<number | undefined>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mock destinations - in real implementation, fetch from API
  const destinations: Destination[] = [
    // These would come from Configuration API
    // { id: 1, name: 'FTP Principal', type: 'ftp', host: 'ftp.example.com' },
    // { id: 2, name: 'SSH Backup', type: 'ssh', host: 'ssh.example.com' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Finalization will be handled by parent component
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call
      onFinalize({ destination_id: selectedDestinationId });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Échec de la finalisation');
      setLoading(false);
    }
  };

  return (
    <div className="wizard-step">
      <h3>Étape 9 : Destination</h3>
      <p className="text-muted">
        Sélectionnez la destination pour l'upload du package final.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Destination</label>
          {destinations.length === 0 ? (
            <div className="alert alert-info" role="alert">
              <strong>Aucune destination configurée</strong>
              <p className="mb-0 mt-2">
                Le package sera créé localement dans le répertoire de sortie.
                Vous pouvez configurer des destinations FTP/SSH dans les paramètres de l'application.
              </p>
            </div>
          ) : (
            <div className="list-group">
              {destinations.map((dest) => (
                <label
                  key={dest.id}
                  className={`list-group-item list-group-item-action ${
                    selectedDestinationId === dest.id ? 'active' : ''
                  }`}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="form-check">
                    <input
                      className="form-check-input"
                      type="radio"
                      name="destination"
                      id={`destination-${dest.id}`}
                      checked={selectedDestinationId === dest.id}
                      onChange={() => setSelectedDestinationId(dest.id)}
                    />
                    <label
                      className="form-check-label w-100"
                      htmlFor={`destination-${dest.id}`}
                    >
                      <strong>{dest.name}</strong>
                      <div className="small text-muted">
                        {dest.type.toUpperCase()} - {dest.host}
                      </div>
                    </label>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        <div className="alert alert-warning" role="alert">
          <strong>Attention :</strong> La finalisation créera le package et le mettra en ligne.
          Assurez-vous que toutes les informations sont correctes avant de continuer.
        </div>

        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        <div className="d-flex justify-content-end gap-2 mt-3">
          <button
            type="submit"
            className="btn btn-success"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                Finalisation...
              </>
            ) : (
              'Finaliser Release'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
