/** Wizard Step 6: Metadata enrichment with editable form. */

import { useState, useEffect } from 'react';

interface StepEnrichmentProps {
  analysis: Record<string, unknown>;
  onNext: (data: { enriched_metadata: Record<string, unknown> }) => void;
}

/**
 * Step 6: Metadata enrichment component with editable form.
 */
export function StepEnrichment({ analysis, onNext }: StepEnrichmentProps) {
  const [metadata, setMetadata] = useState<Record<string, unknown>>({
    title: '',
    author: '',
    isbn: '',
    year: '',
    publisher: '',
    language: '',
    format: '',
    ...analysis,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    // Pre-fill with analysis data
    setMetadata(prev => ({
      ...prev,
      ...analysis,
    }));
  }, [analysis]);

  const handleChange = (field: string, value: unknown) => {
    setMetadata(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!metadata.title || String(metadata.title).trim() === '') {
      newErrors.title = 'Le titre est requis';
    }
    
    if (!metadata.author || String(metadata.author).trim() === '') {
      newErrors.author = 'L\'auteur est requis';
    }

    if (metadata.isbn && String(metadata.isbn).trim() !== '') {
      const isbnRegex = /^(?:\d{10}|\d{13}|(?:\d{9}X))$/;
      if (!isbnRegex.test(String(metadata.isbn).replace(/[-\s]/g, ''))) {
        newErrors.isbn = 'ISBN invalide (format: 10 ou 13 chiffres)';
      }
    }

    if (metadata.year) {
      const year = Number(metadata.year);
      if (isNaN(year) || year < 1900 || year > new Date().getFullYear() + 1) {
        newErrors.year = `Année invalide (1900-${new Date().getFullYear() + 1})`;
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onNext({ enriched_metadata: metadata });
    }
  };

  return (
    <div className="wizard-step">
      <h3>Étape 6 : Enrichissement Métadonnées</h3>
      <p className="text-muted">
        Modifiez ou complétez les métadonnées détectées lors de l'analyse.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label htmlFor="title" className="form-label">
              Titre <span className="text-danger">*</span>
            </label>
            <input
              type="text"
              className={`form-control ${errors.title ? 'is-invalid' : ''}`}
              id="title"
              value={String(metadata.title || '')}
              onChange={(e) => handleChange('title', e.target.value)}
              required
              aria-invalid={errors.title ? 'true' : 'false'}
              aria-describedby={errors.title ? 'title-error' : undefined}
            />
            {errors.title && (
              <div id="title-error" className="invalid-feedback" role="alert">
                {errors.title}
              </div>
            )}
          </div>

          <div className="col-md-6 mb-3">
            <label htmlFor="author" className="form-label">
              Auteur <span className="text-danger">*</span>
            </label>
            <input
              type="text"
              className={`form-control ${errors.author ? 'is-invalid' : ''}`}
              id="author"
              value={String(metadata.author || '')}
              onChange={(e) => handleChange('author', e.target.value)}
              required
              aria-invalid={errors.author ? 'true' : 'false'}
              aria-describedby={errors.author ? 'author-error' : undefined}
            />
            {errors.author && (
              <div id="author-error" className="invalid-feedback" role="alert">
                {errors.author}
              </div>
            )}
          </div>
        </div>

        <div className="row">
          <div className="col-md-6 mb-3">
            <label htmlFor="isbn" className="form-label">ISBN</label>
            <input
              type="text"
              className={`form-control ${errors.isbn ? 'is-invalid' : ''}`}
              id="isbn"
              value={String(metadata.isbn || '')}
              onChange={(e) => handleChange('isbn', e.target.value)}
              placeholder="978-0123456789"
              aria-invalid={errors.isbn ? 'true' : 'false'}
              aria-describedby={errors.isbn ? 'isbn-error' : undefined}
            />
            {errors.isbn && (
              <div id="isbn-error" className="invalid-feedback" role="alert">
                {errors.isbn}
              </div>
            )}
            <div className="form-text">Format: 10 ou 13 chiffres (avec ou sans tirets)</div>
          </div>

          <div className="col-md-6 mb-3">
            <label htmlFor="year" className="form-label">Année</label>
            <input
              type="number"
              className={`form-control ${errors.year ? 'is-invalid' : ''}`}
              id="year"
              value={String(metadata.year || '')}
              onChange={(e) => handleChange('year', e.target.value)}
              placeholder="2024"
              min="1900"
              max={new Date().getFullYear() + 1}
              aria-invalid={errors.year ? 'true' : 'false'}
              aria-describedby={errors.year ? 'year-error' : undefined}
            />
            {errors.year && (
              <div id="year-error" className="invalid-feedback" role="alert">
                {errors.year}
              </div>
            )}
          </div>
        </div>

        <div className="row">
          <div className="col-md-6 mb-3">
            <label htmlFor="publisher" className="form-label">Éditeur</label>
            <input
              type="text"
              className="form-control"
              id="publisher"
              value={String(metadata.publisher || '')}
              onChange={(e) => handleChange('publisher', e.target.value)}
            />
          </div>

          <div className="col-md-6 mb-3">
            <label htmlFor="language" className="form-label">Langue</label>
            <select
              className="form-select"
              id="language"
              value={String(metadata.language || '')}
              onChange={(e) => handleChange('language', e.target.value)}
            >
              <option value="">Sélectionner...</option>
              <option value="fr">Français</option>
              <option value="en">Anglais</option>
              <option value="es">Espagnol</option>
              <option value="de">Allemand</option>
              <option value="it">Italien</option>
              <option value="pt">Portugais</option>
            </select>
          </div>
        </div>

        <div className="mb-3">
          <label htmlFor="format" className="form-label">Format</label>
          <select
            className="form-select"
            id="format"
            value={String(metadata.format || '')}
            onChange={(e) => handleChange('format', e.target.value)}
          >
            <option value="">Sélectionner...</option>
            <option value="EPUB">EPUB</option>
            <option value="PDF">PDF</option>
            <option value="MOBI">MOBI</option>
            <option value="AZW3">AZW3</option>
            <option value="CBZ">CBZ</option>
          </select>
        </div>

        <div className="alert alert-info" role="alert">
          Les métadonnées peuvent être enrichies via des APIs externes dans une version future.
        </div>

        <div className="d-flex justify-content-end gap-2 mt-3">
          <button
            type="submit"
            className="btn btn-primary"
          >
            Suivant
          </button>
        </div>
      </form>
    </div>
  );
}
