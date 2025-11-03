/** Wizard container component. */

import { useState } from 'react';
import { WizardNavigation } from './WizardNavigation';
import { WizardProgress } from './WizardProgress';

interface WizardContainerProps {
  children: React.ReactNode;
  currentStep: number;
  totalSteps: number;
  onStepChange: (step: number) => void;
}

/**
 * Wizard container component with navigation and progress.
 */
export function WizardContainer({
  children,
  currentStep,
  totalSteps,
  onStepChange,
}: WizardContainerProps) {
  const [jobId, setJobId] = useState<number | null>(null);

  return (
    <div className="wizard-container">
      <WizardProgress currentStep={currentStep} totalSteps={totalSteps} />
      <div className="wizard-content">{children}</div>
      <WizardNavigation
        currentStep={currentStep}
        totalSteps={totalSteps}
        onPrevious={() => onStepChange(Math.max(1, currentStep - 1))}
        onNext={() => onStepChange(Math.min(totalSteps, currentStep + 1))}
        canGoNext={true}
      />
    </div>
  );
}
