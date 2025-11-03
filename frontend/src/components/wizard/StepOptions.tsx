/** Wizard Step 8: Packaging options. */

interface StepOptionsProps {
  onNext: (data: { options: Record<string, unknown> }) => void;
}

/**
 * Step 8: Packaging options component.
 */
export function StepOptions({ onNext }: StepOptionsProps) {
  const handleNext = () => {
    onNext({ options: {} });
  };

  return (
    <div className="wizard-step">
      <h3>Étape 8 : Options Packaging</h3>
      <p className="text-muted">
        Options de packaging avancées. Cette fonctionnalité sera implémentée dans les prochaines
        phases.
      </p>
      <div className="alert alert-info">Options par défaut seront utilisées.</div>
    </div>
  );
}
