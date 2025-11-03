/** Wizard Step 6: Metadata enrichment. */

interface StepEnrichmentProps {
  analysis: Record<string, unknown>;
  onNext: (data: { enriched_metadata: Record<string, unknown> }) => void;
}

/**
 * Step 6: Metadata enrichment component.
 */
export function StepEnrichment({ analysis, onNext }: StepEnrichmentProps) {
  const handleNext = () => {
    onNext({ enriched_metadata: analysis });
  };

  return (
    <div className="wizard-step">
      <h3>Étape 6 : Enrichissement Métadonnées</h3>
      <p className="text-muted">
        Les métadonnées peuvent être enrichies via des APIs externes. Cette fonctionnalité sera
        implémentée dans les prochaines phases.
      </p>
      <div className="alert alert-info">
        Les métadonnées analysées seront utilisées telles quelles pour le packaging.
      </div>
    </div>
  );
}
