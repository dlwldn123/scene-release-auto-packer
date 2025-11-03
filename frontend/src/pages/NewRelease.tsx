/** New release wizard page component. */

import { useState } from 'react';
import { PageLayout } from '../components/PageLayout';
import { WizardContainer } from '../components/WizardContainer';
import { StepAnalysis } from '../components/wizard/StepAnalysis';
import { StepDestination } from '../components/wizard/StepDestination';
import { StepEnrichment } from '../components/wizard/StepEnrichment';
import { StepFileSelection } from '../components/wizard/StepFileSelection';
import { StepGroup } from '../components/wizard/StepGroup';
import { StepOptions } from '../components/wizard/StepOptions';
import { StepReleaseType } from '../components/wizard/StepReleaseType';
import { StepRules } from '../components/wizard/StepRules';
import { StepTemplates } from '../components/wizard/StepTemplates';

const TOTAL_STEPS = 9;

/**
 * New release wizard page component.
 */
export function NewRelease() {
  const [currentStep, setCurrentStep] = useState(1);
  const [wizardData, setWizardData] = useState<Record<string, unknown>>({});

  const handleStepData = (step: number, data: Record<string, unknown>) => {
    setWizardData((prev) => ({ ...prev, [`step${step}`]: data }));
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <StepGroup
            initialValue={(wizardData.step1 as { group?: string })?.group}
            onNext={(data) => {
              handleStepData(1, data);
              setCurrentStep(2);
            }}
          />
        );
      case 2:
        return (
          <StepReleaseType
            initialValue={(wizardData.step2 as { release_type?: string })?.release_type}
            onNext={(data) => {
              handleStepData(2, data);
              setCurrentStep(3);
            }}
          />
        );
      case 3:
        return (
          <StepRules
            releaseType={(wizardData.step2 as { release_type?: string })?.release_type || ''}
            initialValue={(wizardData.step3 as { rule_id?: number })?.rule_id}
            onNext={(data) => {
              handleStepData(3, data);
              setCurrentStep(4);
            }}
          />
        );
      case 4:
        return (
          <StepFileSelection
            onNext={(data) => {
              handleStepData(4, data);
              setCurrentStep(5);
            }}
          />
        );
      case 5:
        return (
          <StepAnalysis
            filePath={(wizardData.step4 as { file_path?: string })?.file_path || ''}
            onNext={(data) => {
              handleStepData(5, data);
              setCurrentStep(6);
            }}
          />
        );
      case 6:
        return (
          <StepEnrichment
            analysis={(wizardData.step5 as { analysis?: Record<string, unknown> })?.analysis || {}}
            onNext={(data) => {
              handleStepData(6, data);
              setCurrentStep(7);
            }}
          />
        );
      case 7:
        return (
          <StepTemplates
            onNext={(data) => {
              handleStepData(7, data);
              setCurrentStep(8);
            }}
          />
        );
      case 8:
        return (
          <StepOptions
            onNext={(data) => {
              handleStepData(8, data);
              setCurrentStep(9);
            }}
          />
        );
      case 9:
        return (
          <StepDestination
            onFinalize={(data) => {
              handleStepData(9, data);
              // TODO: Submit final wizard data
              alert('Wizard complété ! (À implémenter : soumission finale)');
            }}
          />
        );
      default:
        return <div className="alert alert-danger">Étape invalide</div>;
    }
  };

  return (
    <PageLayout title="Nouvelle Release" description="Créer une nouvelle release via le wizard">
      <WizardContainer
        currentStep={currentStep}
        totalSteps={TOTAL_STEPS}
        onStepChange={setCurrentStep}
      >
        {renderStep()}
      </WizardContainer>
    </PageLayout>
  );
}
