/** Wizard Step 2: Release type selection. */

interface StepReleaseTypeProps {
  initialValue?: string;
  onNext: (data: { release_type: string }) => void;
}

const RELEASE_TYPES = [
  { value: 'EBOOK', label: 'EBOOK', description: 'Livres électroniques (EPUB, PDF, MOBI)' },
  { value: 'TV', label: 'TV', description: 'Séries télévisées' },
  { value: 'DOCS', label: 'DOCS', description: 'Documentaires' },
  { value: 'AUDIOBOOK', label: 'AUDIOBOOK', description: 'Livres audio' },
  { value: 'GAME', label: 'GAME', description: 'Jeux vidéo' },
];

/**
 * Step 2: Release type selection component.
 */
export function StepReleaseType({ initialValue, onNext }: StepReleaseTypeProps) {
  const handleSelect = (releaseType: string) => {
    onNext({ release_type: releaseType });
  };

  return (
    <div className="wizard-step">
      <h3>Étape 2 : Type de Release</h3>
      <p className="text-muted">Sélectionnez le type de release à créer.</p>

      <div className="row g-3">
        {RELEASE_TYPES.map((type) => (
          <div key={type.value} className="col-md-6 col-lg-4">
            <div
              className={`card h-100 cursor-pointer ${
                initialValue === type.value ? 'border-primary' : ''
              }`}
              onClick={() => handleSelect(type.value)}
              style={{ cursor: 'pointer' }}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  handleSelect(type.value);
                }
              }}
            >
              <div className="card-body">
                <h5 className="card-title">{type.label}</h5>
                <p className="card-text text-muted">{type.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
