/** Tests for Navbar component. */

import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { Navbar } from '../Navbar';

describe('Navbar', () => {
  it('should render navigation links', () => {
    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Nouvelle Release')).toBeInTheDocument();
    expect(screen.getByText('Liste Releases')).toBeInTheDocument();
  });

  it('should render theme toggle', () => {
    render(
      <BrowserRouter>
        <Navbar />
      </BrowserRouter>
    );

    const toggleButton = screen.getByLabelText(/switch to/i);
    expect(toggleButton).toBeInTheDocument();
  });
});
