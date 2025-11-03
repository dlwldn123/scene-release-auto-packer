/** Wizard Step 7: NFO templates. */

interface StepTemplatesProps {
  onNext: (data: { template_id?: number }) => void;
}

/**
 * Step 7: NFO templates selection component.
 */
export function StepTemplates({ onNext }: StepTemplatesProps) {
  const handleNext = () => {
    onNext({});
  };

  return (
    <div className="wizard-step">
      <h3>Étape 7 : Templates NFO</h3>
      <p className="text-muted">
        Sélectionnez un template NFO ou utilisez le template par défaut. Cette fonctionnalité sera
        implémentée dans les prochaines phases.
      </p>
      <div className="alert alert-info">Template par défaut sera utilisé.</div>
    </div>
  );
}
