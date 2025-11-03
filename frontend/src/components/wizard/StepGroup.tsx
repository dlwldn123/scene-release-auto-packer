/** Wizard Step 1: Group selection. */

import { useState } from 'react';

interface StepGroupProps {
  initialValue?: string;
  onNext: (data: { group: string }) => void;
}

/**
 * Step 1: Group selection component.
 */
export function StepGroup({ initialValue = '', onNext }: StepGroupProps) {
  const [group, setGroup] = useState(initialValue);
  const [error, setError] = useState<string | null>(null);

  const validate = (value: string): boolean => {
    if (!value || value.length < 2 || value.length > 30) {
      setError('Le nom du groupe doit contenir entre 2 et 30 caractères');
      return false;
    }

    // Scene group format: alphanumeric and hyphen, no spaces
    const pattern = /^[A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9]$/;
    if (!pattern.test(value)) {
      setError('Format invalide : alphanumérique et tirets uniquement');
      return false;
    }

    setError(null);
    return true;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate(group)) {
      onNext({ group });
    }
  };

  return (
    <div className="wizard-step">
      <h3>Étape 1 : Groupe Scene</h3>
      <p className="text-muted">Saisissez le nom du groupe Scene pour cette release.</p>

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label htmlFor="group" className="form-label">
            Nom du groupe <span className="text-danger">*</span>
          </label>
          <input
            type="text"
            className={`form-control ${error ? 'is-invalid' : ''}`}
            id="group"
            value={group}
            onChange={(e) => {
              setGroup(e.target.value);
              if (error) validate(e.target.value);
            }}
            placeholder="Ex: TestGroup"
            required
            aria-describedby="group-help group-error"
          />
          <div id="group-help" className="form-text">
            Format Scene : alphanumérique et tirets uniquement (2-30 caractères)
          </div>
          {error && (
            <div id="group-error" className="invalid-feedback">
              {error}
            </div>
          )}
        </div>
      </form>
    </div>
  );
}
