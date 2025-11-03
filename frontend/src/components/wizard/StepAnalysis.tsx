/** Wizard Step 5: File analysis. */

import { useEffect, useState } from 'react';

interface StepAnalysisProps {
  filePath: string;
  onNext: (data: { analysis: Record<string, unknown> }) => void;
}

/**
 * Step 5: File analysis component.
 */
export function StepAnalysis({ filePath, onNext }: StepAnalysisProps) {
  const [analyzing, setAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [analysis, setAnalysis] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (filePath) {
      // Simulate analysis
      setAnalyzing(true);
      setProgress(0);

      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            setAnalyzing(false);
            setAnalysis({
              title: 'Sample Book Title',
              author: 'Sample Author',
              isbn: '1234567890',
              format: 'EPUB',
              size: '2.5 MB',
            });
            return 100;
          }
          return prev + 10;
        });
      }, 300);
    }
  }, [filePath]);

  const handleNext = () => {
    if (analysis) {
      onNext({ analysis });
    }
  };

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
      ) : null}
    </div>
  );
}
