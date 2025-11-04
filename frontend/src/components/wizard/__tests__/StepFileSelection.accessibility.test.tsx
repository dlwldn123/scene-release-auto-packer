/** Accessibility tests for StepFileSelection component. */

import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, describe, it, afterEach } from 'vitest';
import { StepFileSelection } from '../wizard/StepFileSelection';

expect.extend(toHaveNoViolations);

describe('StepFileSelection Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <StepFileSelection releaseId={1} onNext={() => {}} />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have accessible form labels', () => {
    const { getByLabelText } = render(
      <StepFileSelection releaseId={1} onNext={() => {}} />
    );
    expect(getByLabelText(/fichier local|url distante/i)).toBeInTheDocument();
  });

  it('should have accessible drag and drop area', () => {
    const { getByRole } = render(
      <StepFileSelection releaseId={1} onNext={() => {}} />
    );
    const dropZone = getByRole('button', { name: /glisser.*déposer|drag.*drop/i });
    expect(dropZone).toBeInTheDocument();
  });
});
