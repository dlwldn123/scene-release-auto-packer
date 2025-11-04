/** Wizard Step 5: File analysis. */

import { useEffect, useState } from 'react';

interface StepAnalysisProps {
  filePath: string;
  analysis?: Record<string, unknown>;
  onNext: () => void;
}

/**
 * Step 5: File analysis component.
 */
export function StepAnalysis({ filePath, analysis, onNext }: StepAnalysisProps) {
  const [analyzing] = useState(false);
  const [progress] = useState(100);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (filePath) {
      // Analysis will be triggered by parent component via onNext
      // This component just displays the results
    }
  }, [filePath]);

  // Analysis is triggered automatically when filePath is available
  // Parent component handles the API call

  return (
    <div className="wizard-step">
      <h3>Étape 5 : Analyse Fichier</h3>
      <p className="text-muted">Analyse du fichier en cours...</p>

      {analyzing ? (
        <div>
          <div className="progress mb-3">
            <div
              className="progress-bar progress-bar-striped progress-bar-animated"
              role="progressbar"
              style={{ width: `${progress}%` }}
            >
              {progress}%
            </div>
          </div>
          <p className="text-center">Extraction des métadonnées...</p>
        </div>
      ) : analysis ? (
        <div>
          <div className="card">
            <div className="card-header">Résultats de l'analyse</div>
            <div className="card-body">
              <dl className="row">
                <dt className="col-sm-3">Titre</dt>
                <dd className="col-sm-9">{analysis.title as string}</dd>
                <dt className="col-sm-3">Auteur</dt>
                <dd className="col-sm-9">{analysis.author as string}</dd>
                <dt className="col-sm-3">ISBN</dt>
                <dd className="col-sm-9">{analysis.isbn as string}</dd>
                <dt className="col-sm-3">Format</dt>
                <dd className="col-sm-9">{analysis.format as string}</dd>
                <dt className="col-sm-3">Taille</dt>
                <dd className="col-sm-9">{analysis.size as string}</dd>
              </dl>
            </div>
          </div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <div className="alert alert-info">
          Analyse en cours... Veuillez patienter.
        </div>
      )}
    </div>
  );
}
