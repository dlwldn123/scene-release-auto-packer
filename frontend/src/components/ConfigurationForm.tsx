/** Configuration form component for create/edit. */

import { useEffect, useState } from 'react';
import {
  configurationsApi,
  Configuration,
  CreateConfigurationData,
  UpdateConfigurationData,
} from '../services/configurations';

interface ConfigurationFormProps {
  configuration?: Configuration | null;
  onSave: () => void;
  onCancel: () => void;
}

/**
 * Configuration form component for create/edit.
 */
export function ConfigurationForm({
  configuration,
  onSave,
  onCancel,
}: ConfigurationFormProps) {
  const [formData, setFormData] = useState<CreateConfigurationData>({
    key: '',
    value: '',
    category: '',
    description: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (configuration) {
      setFormData({
        key: configuration.key,
        value: configuration.value,
        category: configuration.category || '',
        description: configuration.description || '',
      });
    } else {
      setFormData({
        key: '',
        value: '',
        category: '',
        description: '',
      });
    }
    setErrors({});
    setError(null);
  }, [configuration]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.key.trim()) {
      newErrors.key = 'La clé est requise';
    } else if (!/^[A-Z_][A-Z0-9_]*$/.test(formData.key)) {
      newErrors.key =
        'La clé doit commencer par une majuscule et ne contenir que des lettres majuscules, chiffres et underscores';
    }

    if (!formData.value.trim()) {
      newErrors.value = 'La valeur est requise';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (configuration) {
        // Update
        const updateData: UpdateConfigurationData = {
          key: formData.key !== configuration.key ? formData.key : undefined,
          value: formData.value !== configuration.value ? formData.value : undefined,
          category:
            formData.category !== configuration.category
              ? formData.category || undefined
              : undefined,
          description:
            formData.description !== configuration.description
              ? formData.description || undefined
              : undefined,
        };
        await configurationsApi.update(configuration.id, updateData);
      } else {
        // Create
        await configurationsApi.create(formData);
      }
      onSave();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to save configuration'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      <div className="mb-3">
        <label htmlFor="key" className="form-label">
          Clé <span className="text-danger">*</span>
        </label>
        <input
          id="key"
          type="text"
          className={`form-control ${errors.key ? 'is-invalid' : ''}`}
          value={formData.key}
          onChange={e =>
            setFormData({ ...formData, key: e.target.value.toUpperCase() })
          }
          disabled={!!configuration}
          placeholder="EXEMPLE_KEY"
          aria-describedby={errors.key ? 'key-error' : undefined}
          aria-invalid={!!errors.key}
        />
        {errors.key && (
          <div id="key-error" className="invalid-feedback">
            {errors.key}
          </div>
        )}
        {!configuration && (
          <div className="form-text">
            La clé doit commencer par une majuscule et ne contenir que des
            lettres majuscules, chiffres et underscores
          </div>
        )}
      </div>

      <div className="mb-3">
        <label htmlFor="value" className="form-label">
          Valeur <span className="text-danger">*</span>
        </label>
        <textarea
          id="value"
          className={`form-control ${errors.value ? 'is-invalid' : ''}`}
          value={formData.value}
          onChange={e => setFormData({ ...formData, value: e.target.value })}
          rows={3}
          placeholder="Valeur de la configuration"
          aria-describedby={errors.value ? 'value-error' : undefined}
          aria-invalid={!!errors.value}
        />
        {errors.value && (
          <div id="value-error" className="invalid-feedback">
            {errors.value}
          </div>
        )}
      </div>

      <div className="mb-3">
        <label htmlFor="category" className="form-label">
          Catégorie
        </label>
        <input
          id="category"
          type="text"
          className="form-control"
          value={formData.category}
          onChange={e =>
            setFormData({ ...formData, category: e.target.value })
          }
          placeholder="ex: api, ftp, ssh"
        />
      </div>

      <div className="mb-3">
        <label htmlFor="description" className="form-label">
          Description
        </label>
        <textarea
          id="description"
          className="form-control"
          value={formData.description}
          onChange={e =>
            setFormData({ ...formData, description: e.target.value })
          }
          rows={2}
          placeholder="Description de la configuration"
        />
      </div>

      <div className="d-flex gap-2 justify-content-end">
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onCancel}
          disabled={loading}
        >
          Annuler
        </button>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (
            <>
              <span
                className="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              />
              Enregistrement...
            </>
          ) : configuration ? (
            'Mettre à jour'
          ) : (
            'Créer'
          )}
        </button>
      </div>
    </form>
  );
}
