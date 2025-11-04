/** New Release Wizard Page - Complete 9-step wizard. */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { WizardContainer } from '../components/WizardContainer';
import { StepGroup } from '../components/wizard/StepGroup';
import { StepReleaseType } from '../components/wizard/StepReleaseType';
import { StepRules } from '../components/wizard/StepRules';
import { StepFileSelection } from '../components/wizard/StepFileSelection';
import { StepAnalysis } from '../components/wizard/StepAnalysis';
import { StepEnrichment } from '../components/wizard/StepEnrichment';
import { StepTemplates } from '../components/wizard/StepTemplates';
import { StepOptions } from '../components/wizard/StepOptions';
import { StepDestination } from '../components/wizard/StepDestination';
import { wizardApi } from '../services/wizard';

interface WizardData {
  releaseId?: number;
  jobId?: number;
  group?: string;
  releaseType?: string;
  ruleId?: number;
  filePath?: string;
  fileType?: 'local' | 'remote';
  analysis?: Record<string, unknown>;
  enrichedMetadata?: Record<string, unknown>;
  templateId?: number;
  options?: Record<string, unknown>;
  destinationId?: number;
}

const TOTAL_STEPS = 9;

/**
 * New Release Wizard Page - Complete 9-step wizard.
 */
export function NewRelease() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wizardData, setWizardData] = useState<WizardData>({});

  const handleStep1Next = async (data: { group: string }) => {
    setWizardData(prev => ({ ...prev, group: data.group }));
    setCurrentStep(2);
  };

  const handleStep2Next = async (data: { release_type: string }) => {
    setWizardData(prev => ({ ...prev, releaseType: data.release_type }));
    setCurrentStep(3);
  };

  const handleStep3Next = async (data: { rule_id: number }) => {
    setLoading(true);
    setError(null);

    try {
      if (!wizardData.group || !wizardData.releaseType) {
        throw new Error('Group and release type are required');
      }

      const response = await wizardApi.createDraft({
        group: wizardData.group,
        release_type: wizardData.releaseType,
        rule_id: data.rule_id,
      });

      setWizardData(prev => ({
        ...prev,
        releaseId: response.release_id,
        jobId: response.job_id,
        ruleId: data.rule_id,
      }));
      setCurrentStep(4);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create draft');
    } finally {
      setLoading(false);
    }
  };

  const handleStep4Next = async (data: { file_path: string; file_type: 'local' | 'remote' }) => {
    if (!wizardData.releaseId) {
      setError('Release ID not found');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let file: File | string;
      if (data.file_type === 'remote') {
        file = data.file_path;
      } else {
        // Get file from input
        const fileInput = document.querySelector<HTMLInputElement>('input[type="file"]');
        if (!fileInput?.files?.[0]) {
          throw new Error('No file selected');
        }
        file = fileInput.files[0];
      }

      await wizardApi.uploadFile(wizardData.releaseId, file);

      setWizardData(prev => ({
        ...prev,
        filePath: data.file_path,
        fileType: data.file_type,
      }));
      setCurrentStep(5);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    } finally {
      setLoading(false);
    }
  };

  const handleStep5Next = async () => {
    if (!wizardData.releaseId) {
      setError('Release ID not found');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await wizardApi.analyzeFile(wizardData.releaseId);
      setWizardData(prev => ({
        ...prev,
        analysis: response.analysis,
      }));
      setCurrentStep(6);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze file');
    } finally {
      setLoading(false);
    }
  };

  const handleStep6Next = async (data: { enriched_metadata: Record<string, unknown> }) => {
    if (!wizardData.releaseId) {
      setError('Release ID not found');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await wizardApi.updateMetadata(wizardData.releaseId, data.enriched_metadata);
      setWizardData(prev => ({
        ...prev,
        enrichedMetadata: data.enriched_metadata,
      }));
      setCurrentStep(7);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update metadata');
    } finally {
      setLoading(false);
    }
  };

  const handleStep7Next = async (data: { template_id?: number }) => {
    if (!wizardData.releaseId) {
      setError('Release ID not found');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await wizardApi.selectTemplate(wizardData.releaseId, data.template_id);
      setWizardData(prev => ({
        ...prev,
        templateId: data.template_id,
      }));
      setCurrentStep(8);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to select template');
    } finally {
      setLoading(false);
    }
  };

  const handleStep8Next = async (data: { options: Record<string, unknown> }) => {
    if (!wizardData.releaseId) {
      setError('Release ID not found');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await wizardApi.updateOptions(wizardData.releaseId, data.options);
      setWizardData(prev => ({
        ...prev,
        options: data.options,
      }));
      setCurrentStep(9);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update options');
    } finally {
      setLoading(false);
    }
  };

  const handleStep9Finalize = async (data: { destination_id?: number }) => {
    if (!wizardData.releaseId) {
      setError('Release ID not found');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await wizardApi.finalizeRelease(wizardData.releaseId, data.destination_id);
      navigate('/releases');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to finalize release');
      setLoading(false);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <StepGroup onNext={handleStep1Next} />;
      case 2:
        return (
          <StepReleaseType
            releaseType={wizardData.releaseType}
            onNext={handleStep2Next}
          />
        );
      case 3:
        return (
          <StepRules
            releaseType={wizardData.releaseType}
            onNext={handleStep3Next}
          />
        );
      case 4:
        return <StepFileSelection onNext={handleStep4Next} />;
      case 5:
        return (
          <StepAnalysis
            filePath={wizardData.filePath || ''}
            analysis={wizardData.analysis}
            onNext={handleStep5Next}
          />
        );
      case 6:
        return (
          <StepEnrichment
            analysis={wizardData.analysis || {}}
            onNext={handleStep6Next}
          />
        );
      case 7:
        return (
          <StepTemplates
            releaseId={wizardData.releaseId}
            onNext={handleStep7Next}
          />
        );
      case 8:
        return <StepOptions onNext={handleStep8Next} />;
      case 9:
        return <StepDestination onFinalize={handleStep9Finalize} />;
      default:
        return null;
    }
  };

  return (
    <div className="new-release-page">
      <h1>Nouvelle Release</h1>
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}
      {loading && (
        <div className="alert alert-info" role="alert">
          Traitement en cours...
        </div>
      )}
      <WizardContainer
        currentStep={currentStep}
        totalSteps={TOTAL_STEPS}
        onStepChange={setCurrentStep}
      >
        {renderStep()}
      </WizardContainer>
    </div>
  );
}
