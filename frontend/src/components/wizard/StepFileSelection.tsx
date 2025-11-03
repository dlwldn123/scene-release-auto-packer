/** Wizard Step 4: File selection. */

import { useState } from 'react';

interface StepFileSelectionProps {
  onNext: (data: { file_path: string; file_type: 'local' | 'remote' }) => void;
}

/**
 * Step 4: File selection component.
 */
export function StepFileSelection({ onNext }: StepFileSelectionProps) {
  const [fileType, setFileType] = useState<'local' | 'remote'>('local');
  const [filePath, setFilePath] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFilePath(file.name);
      setError(null);
    }
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setFilePath(url);
    if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
      setError('URL doit commencer par http:// ou https://');
    } else {
      setError(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!filePath) {
      setError('Veuillez sélectionner un fichier ou entrer une URL');
      return;
    }
    if (fileType === 'remote' && error) {
      return;
    }
    onNext({ file_path: filePath, file_type: fileType });
  };

  return (
    <div className="wizard-step">
      <h3>Étape 4 : Sélection Fichier</h3>
      <p className="text-muted">Sélectionnez le fichier à packager (local ou distant).</p>

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <div className="btn-group" role="group">
            <input
              type="radio"
              className="btn-check"
              name="fileType"
              id="fileTypeLocal"
              checked={fileType === 'local'}
              onChange={() => setFileType('local')}
            />
            <label className="btn btn-outline-primary" htmlFor="fileTypeLocal">
              Fichier Local
            </label>

            <input
              type="radio"
              className="btn-check"
              name="fileType"
              id="fileTypeRemote"
              checked={fileType === 'remote'}
              onChange={() => setFileType('remote')}
            />
            <label className="btn btn-outline-primary" htmlFor="fileTypeRemote">
              URL Distante
            </label>
          </div>
        </div>

        {fileType === 'local' ? (
          <div className="mb-3">
            <label htmlFor="file" className="form-label">
              Fichier <span className="text-danger">*</span>
            </label>
            <input
              type="file"
              className="form-control"
              id="file"
              onChange={handleFileChange}
              required
            />
            <div className="form-text">Taille maximale : 20GB</div>
          </div>
        ) : (
          <div className="mb-3">
            <label htmlFor="url" className="form-label">
              URL <span className="text-danger">*</span>
            </label>
            <input
              type="url"
              className={`form-control ${error ? 'is-invalid' : ''}`}
              id="url"
              value={filePath}
              onChange={handleUrlChange}
              placeholder="https://example.com/file.epub"
              required
            />
            {error && <div className="invalid-feedback">{error}</div>}
          </div>
        )}
      </form>
    </div>
  );
}
