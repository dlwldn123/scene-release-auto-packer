/** Wizard navigation component. */

interface WizardNavigationProps {
  currentStep: number;
  totalSteps: number;
  onPrevious: () => void;
  onNext: () => void;
  canGoNext: boolean;
}

/**
 * Wizard navigation buttons component.
 */
export function WizardNavigation({
  currentStep,
  totalSteps,
  onPrevious,
  onNext,
  canGoNext,
}: WizardNavigationProps) {
  return (
    <div className="wizard-navigation d-flex justify-content-between mt-4">
      <button
        type="button"
        className="btn btn-secondary"
        onClick={onPrevious}
        disabled={currentStep === 1}
      >
        Précédent
      </button>
      <div>
        {currentStep < totalSteps ? (
          <button
            type="button"
            className="btn btn-primary"
            onClick={onNext}
            disabled={!canGoNext}
          >
            Suivant
          </button>
        ) : (
          <button type="button" className="btn btn-success" disabled={!canGoNext}>
            Finaliser
          </button>
        )}
      </div>
    </div>
  );
}
