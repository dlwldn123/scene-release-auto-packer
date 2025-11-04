/** Wizard Step 4: File selection with drag & drop support. */

import { useState, useCallback } from 'react';
import { wizardApi } from '../../services/wizard';

interface StepFileSelectionProps {
  releaseId?: number;
  onNext: (data: { file_path: string; file_type: 'local' | 'remote' }) => void;
}

const MAX_FILE_SIZE = 20 * 1024 * 1024 * 1024; // 20GB

/**
 * Step 4: File selection component with drag & drop and progress bar.
 */
export function StepFileSelection({ releaseId, onNext }: StepFileSelectionProps) {
  const [fileType, setFileType] = useState<'local' | 'remote'>('local');
  const [filePath, setFilePath] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > MAX_FILE_SIZE) {
        setError(`Fichier trop volumineux (max ${MAX_FILE_SIZE / (1024 * 1024 * 1024)}GB)`);
        return;
      }
      setSelectedFile(file);
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

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      if (file.size > MAX_FILE_SIZE) {
        setError(`Fichier trop volumineux (max ${MAX_FILE_SIZE / (1024 * 1024 * 1024)}GB)`);
        return;
      }
      setSelectedFile(file);
      setFilePath(file.name);
      setError(null);
    }
  }, []);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${Math.round(bytes / Math.pow(k, i) * 100) / 100} ${sizes[i]}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (fileType === 'remote') {
      if (!filePath || !filePath.startsWith('http')) {
        setError('Veuillez entrer une URL valide');
        return;
      }
      if (!releaseId) {
        setError('Release ID manquant');
        return;
      }

      setLoading(true);
      try {
        await wizardApi.uploadFile(releaseId, filePath);
        onNext({ file_path: filePath, file_type: 'remote' });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Échec de l\'upload');
      } finally {
        setLoading(false);
      }
    } else {
      if (!selectedFile) {
        setError('Veuillez sélectionner un fichier');
        return;
      }
      if (!releaseId) {
        setError('Release ID manquant');
        return;
      }

      setLoading(true);
      setUploadProgress(0);

      try {
        // Simulate upload progress (in real implementation, use XMLHttpRequest for progress)
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => {
            if (prev >= 90) {
              clearInterval(progressInterval);
              return prev;
            }
            return prev + 10;
          });
        }, 200);

        await wizardApi.uploadFile(releaseId, selectedFile);
        setUploadProgress(100);
        clearInterval(progressInterval);

        setTimeout(() => {
          onNext({ file_path: selectedFile.name, file_type: 'local' });
        }, 500);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Échec de l\'upload');
        setUploadProgress(0);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="wizard-step">
      <h3>Étape 4 : Sélection Fichier</h3>
      <p className="text-muted">
        Sélectionnez le fichier à packager (local ou distant).
      </p>

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <div className="btn-group" role="group" aria-label="Type de fichier">
            <input
              type="radio"
              className="btn-check"
              name="fileType"
              id="fileTypeLocal"
              checked={fileType === 'local'}
              onChange={() => {
                setFileType('local');
                setError(null);
              }}
              disabled={loading}
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
              onChange={() => {
                setFileType('remote');
                setError(null);
              }}
              disabled={loading}
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
            <div
              className={`border rounded p-4 text-center ${isDragging ? 'border-primary bg-light' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              role="button"
              tabIndex={0}
              aria-label="Zone de dépôt de fichier"
            >
              <input
                type="file"
                className="form-control d-none"
                id="file"
                onChange={handleFileChange}
                disabled={loading}
                required
              />
              <label htmlFor="file" className="btn btn-outline-primary mb-2">
                Sélectionner un fichier
              </label>
              <p className="text-muted mb-0">
                ou glissez-déposez le fichier ici
              </p>
              {selectedFile && (
                <div className="mt-3">
                  <p className="mb-1">
                    <strong>{selectedFile.name}</strong>
                  </p>
                  <p className="text-muted mb-0">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              )}
            </div>
            <div className="form-text">Taille maximale : 20GB</div>
            {loading && uploadProgress > 0 && (
              <div className="mt-3">
                <div className="progress">
                  <div
                    className="progress-bar progress-bar-striped progress-bar-animated"
                    role="progressbar"
                    style={{ width: `${uploadProgress}%` }}
                    aria-valuenow={uploadProgress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  >
                    {uploadProgress}%
                  </div>
                </div>
              </div>
            )}
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
              disabled={loading}
              required
              aria-invalid={error ? 'true' : 'false'}
              aria-describedby={error ? 'url-error' : undefined}
            />
            {error && (
              <div id="url-error" className="invalid-feedback" role="alert">
                {error}
              </div>
            )}
            <div className="form-text">URL du fichier distant à télécharger</div>
          </div>
        )}

        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        <div className="d-flex justify-content-end gap-2 mt-3">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !filePath || (fileType === 'remote' && !!error)}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                {fileType === 'local' ? 'Upload en cours...' : 'Téléchargement...'}
              </>
            ) : (
              'Suivant'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
