/** Wizard Step 9: Destination. */

interface StepDestinationProps {
  onFinalize: (data: { destination_id?: number }) => void;
}

/**
 * Step 9: Destination selection component.
 */
export function StepDestination({ onFinalize }: StepDestinationProps) {
  const handleFinalize = () => {
    onFinalize({});
  };

  return (
    <div className="wizard-step">
      <h3>Étape 9 : Destination</h3>
      <p className="text-muted">
        Sélectionnez la destination pour l'upload du package. Cette fonctionnalité sera implémentée
        dans les prochaines phases.
      </p>
      <div className="alert alert-info">Aucune destination configurée. Le package sera créé localement.</div>
    </div>
  );
}
