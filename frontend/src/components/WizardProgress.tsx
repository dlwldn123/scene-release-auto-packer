/** Wizard progress component. */

interface WizardProgressProps {
  currentStep: number;
  totalSteps: number;
}

const STEP_LABELS = [
  'Groupe',
  'Type',
  'Règle',
  'Fichier',
  'Analyse',
  'Enrichissement',
  'Templates',
  'Options',
  'Destination',
];

/**
 * Wizard progress indicator component.
 */
export function WizardProgress({ currentStep, totalSteps }: WizardProgressProps) {
  return (
    <div className="wizard-progress mb-4">
      <div className="progress" style={{ height: '30px' }}>
        {Array.from({ length: totalSteps }, (_, i) => i + 1).map((step) => (
          <div
            key={step}
            className={`progress-step ${step <= currentStep ? 'active' : ''} ${
              step === currentStep ? 'current' : ''
            }`}
            style={{
              width: `${100 / totalSteps}%`,
              backgroundColor: step <= currentStep ? '#0d6efd' : '#e9ecef',
              display: 'inline-block',
              height: '100%',
              borderRight: '1px solid #fff',
            }}
            title={STEP_LABELS[step - 1] || `Étape ${step}`}
          />
        ))}
      </div>
      <div className="text-center mt-2">
        <small className="text-muted">
          Étape {currentStep} sur {totalSteps} : {STEP_LABELS[currentStep - 1]}
        </small>
      </div>
    </div>
  );
}
