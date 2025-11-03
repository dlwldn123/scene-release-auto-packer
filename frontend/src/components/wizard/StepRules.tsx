/** Wizard Step 3: Rule selection. */

import { useEffect, useState } from 'react';
import { wizardApi } from '../../services/wizard';

interface StepRulesProps {
  releaseType: string;
  initialValue?: number;
  onNext: (data: { rule_id: number }) => void;
}

/**
 * Step 3: Rule selection component.
 */
export function StepRules({ releaseType, initialValue, onNext }: StepRulesProps) {
  const [rules, setRules] = useState<Array<{ id: number; name: string }>>([]);
  const [selectedRuleId, setSelectedRuleId] = useState<number | null>(initialValue || null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRules = async () => {
      try {
        setLoading(true);
        const response = await wizardApi.listRules(releaseType);
        setRules(response.data?.rules || []);
      } catch (err) {
        console.error('Failed to load rules:', err);
      } finally {
        setLoading(false);
      }
    };

    if (releaseType) {
      fetchRules();
    }
  }, [releaseType]);

  const handleSelect = (ruleId: number) => {
    setSelectedRuleId(ruleId);
    onNext({ rule_id: ruleId });
  };

  if (loading) {
    return (
      <div className="wizard-step">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="wizard-step">
      <h3>Étape 3 : Règle Scene</h3>
      <p className="text-muted">Sélectionnez la règle Scene à appliquer pour ce type de release.</p>

      {rules.length === 0 ? (
        <div className="alert alert-info">
          Aucune règle disponible pour le type {releaseType}. Veuillez charger des règles depuis
          scenerules.org.
        </div>
      ) : (
        <div className="list-group">
          {rules.map((rule) => (
            <button
              key={rule.id}
              type="button"
              className={`list-group-item list-group-item-action ${
                selectedRuleId === rule.id ? 'active' : ''
              }`}
              onClick={() => handleSelect(rule.id)}
            >
              {rule.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
