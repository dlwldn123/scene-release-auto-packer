/** Wizard Step 5: File analysis with results display. */

import { useEffect } from 'react';

interface StepAnalysisProps {
  filePath: string;
  analysis?: Record<string, unknown>;
  onNext: () => void;
  loading?: boolean;
}

/**
 * Step 5: File analysis component displaying analysis results.
 */
export function StepAnalysis({ filePath, analysis, onNext, loading = false }: StepAnalysisProps) {
  useEffect(() => {
    // Analysis is triggered automatically when filePath is available
    // Parent component handles the API call
  }, [filePath]);

  const formatValue = (value: unknown): string => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  };

  return (
    <div className="wizard-step">
      <h3>Étape 5 : Analyse Fichier</h3>
      <p className="text-muted">Résultats de l'analyse du fichier.</p>

      {loading ? (
        <div>
          <div className="progress mb-3">
            <div
              className="progress-bar progress-bar-striped progress-bar-animated"
              role="progressbar"
              style={{ width: '100%' }}
              aria-valuenow={100}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              Analyse en cours...
            </div>
          </div>
          <p className="text-center">Extraction des métadonnées...</p>
        </div>
      ) : analysis ? (
        <div>
          <div className="card mb-3">
            <div className="card-header">
              <h5 className="mb-0">Résultats de l'analyse</h5>
            </div>
            <div className="card-body">
              <dl className="row">
                {analysis.filename && (
                  <>
                    <dt className="col-sm-3">Nom du fichier</dt>
                    <dd className="col-sm-9">{formatValue(analysis.filename)}</dd>
                  </>
                )}
                {analysis.file_path && (
                  <>
                    <dt className="col-sm-3">Chemin</dt>
                    <dd className="col-sm-9">
                      <code>{formatValue(analysis.file_path)}</code>
                    </dd>
                  </>
                )}
                {analysis.file_size && (
                  <>
                    <dt className="col-sm-3">Taille</dt>
                    <dd className="col-sm-9">{formatValue(analysis.file_size)}</dd>
                  </>
                )}
                {analysis.detected_group && (
                  <>
                    <dt className="col-sm-3">Groupe détecté</dt>
                    <dd className="col-sm-9">{formatValue(analysis.detected_group)}</dd>
                  </>
                )}
                {analysis.detected_author && (
                  <>
                    <dt className="col-sm-3">Auteur détecté</dt>
                    <dd className="col-sm-9">{formatValue(analysis.detected_author)}</dd>
                  </>
                )}
                {analysis.title && (
                  <>
                    <dt className="col-sm-3">Titre</dt>
                    <dd className="col-sm-9">{formatValue(analysis.title)}</dd>
                  </>
                )}
                {analysis.author && (
                  <>
                    <dt className="col-sm-3">Auteur</dt>
                    <dd className="col-sm-9">{formatValue(analysis.author)}</dd>
                  </>
                )}
                {analysis.isbn && (
                  <>
                    <dt className="col-sm-3">ISBN</dt>
                    <dd className="col-sm-9">{formatValue(analysis.isbn)}</dd>
                  </>
                )}
                {analysis.format && (
                  <>
                    <dt className="col-sm-3">Format</dt>
                    <dd className="col-sm-9">{formatValue(analysis.format)}</dd>
                  </>
                )}
              </dl>
            </div>
          </div>
          <div className="alert alert-info" role="alert">
            Les métadonnées détectées peuvent être modifiées à l'étape suivante.
          </div>
        </div>
      ) : (
        <div className="alert alert-warning" role="alert">
          Aucune analyse disponible. Veuillez vérifier que le fichier a été uploadé correctement.
        </div>
      )}

      {analysis && (
        <div className="d-flex justify-content-end gap-2 mt-3">
          <button
            type="button"
            className="btn btn-primary"
            onClick={onNext}
            disabled={loading}
          >
            Suivant
          </button>
        </div>
      )}
    </div>
  );
}
