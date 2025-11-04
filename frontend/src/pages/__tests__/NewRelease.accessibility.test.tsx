/** Accessibility tests for NewRelease wizard page. */

import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { expect, describe, it } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { NewRelease } from '../../pages/NewRelease';

expect.extend(toHaveNoViolations);

describe('NewRelease Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <BrowserRouter>
        <NewRelease />
      </BrowserRouter>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have accessible navigation', () => {
    const { getByRole } = render(
      <BrowserRouter>
        <NewRelease />
      </BrowserRouter>
    );
    const nav = getByRole('navigation', { name: /wizard|étapes/i });
    expect(nav).toBeInTheDocument();
  });

  it('should have accessible step indicators', () => {
    const { getAllByRole } = render(
      <BrowserRouter>
        <NewRelease />
      </BrowserRouter>
    );
    const stepIndicators = getAllByRole('tab', { name: /étape \d+/i });
    expect(stepIndicators.length).toBeGreaterThan(0);
  });
});
