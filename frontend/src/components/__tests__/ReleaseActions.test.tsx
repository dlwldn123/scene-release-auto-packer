/** Tests for ReleaseActions component. */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { ReleaseActions } from '../ReleaseActions';
import { releasesApi } from '../../services/releases';

// Mock releasesApi
jest.mock('../../services/releases', () => ({
  releasesApi: {
    nfofix: jest.fn(),
    readnfo: jest.fn(),
    repack: jest.fn(),
    dirfix: jest.fn(),
  },
}));

const mockReleasesApi = releasesApi as jest.Mocked<typeof releasesApi>;

describe('ReleaseActions', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock window.prompt for repack
    window.prompt = jest.fn();
  });

  const renderComponent = (props = {}) => {
    return render(
      <BrowserRouter>
        <ReleaseActions releaseId={1} {...props} />
      </BrowserRouter>
    );
  };

  it('should render all action buttons', () => {
    renderComponent();

    expect(screen.getByLabelText('Corriger le fichier NFO')).toBeInTheDocument();
    expect(screen.getByLabelText('Lire NFO et régénérer')).toBeInTheDocument();
    expect(screen.getByLabelText('Repackager la release')).toBeInTheDocument();
    expect(screen.getByLabelText('Corriger la structure de répertoires')).toBeInTheDocument();
  });

  it('should call nfofix API when NFOFIX button clicked', async () => {
    mockReleasesApi.nfofix.mockResolvedValue({
      data: { message: 'Success', job_id: 1 },
    });

    renderComponent();

    const button = screen.getByLabelText('Corriger le fichier NFO');
    await userEvent.click(button);

    await waitFor(() => {
      expect(mockReleasesApi.nfofix).toHaveBeenCalledWith(1);
    });
  });

  it('should call readnfo API when READNFO button clicked', async () => {
    mockReleasesApi.readnfo.mockResolvedValue({
      data: { message: 'Success', job_id: 1 },
    });

    renderComponent();

    const button = screen.getByLabelText('Lire NFO et régénérer');
    await userEvent.click(button);

    await waitFor(() => {
      expect(mockReleasesApi.readnfo).toHaveBeenCalledWith(1);
    });
  });

  it('should call dirfix API when DIRFIX button clicked', async () => {
    mockReleasesApi.dirfix.mockResolvedValue({
      data: { message: 'Success', job_id: 1 },
    });

    renderComponent();

    const button = screen.getByLabelText('Corriger la structure de répertoires');
    await userEvent.click(button);

    await waitFor(() => {
      expect(mockReleasesApi.dirfix).toHaveBeenCalledWith(1);
    });
  });

  it('should call repack API with options when REPACK button clicked', async () => {
    (window.prompt as jest.Mock).mockReturnValue('100');
    mockReleasesApi.repack.mockResolvedValue({
      data: { message: 'Success', job_id: 1 },
    });

    renderComponent();

    const button = screen.getByLabelText('Repackager la release');
    await userEvent.click(button);

    await waitFor(() => {
      expect(mockReleasesApi.repack).toHaveBeenCalledWith(1, { zip_size: 100 });
    });
  });

  it('should display error message on API error', async () => {
    mockReleasesApi.nfofix.mockRejectedValue(new Error('API Error'));

    renderComponent();

    const button = screen.getByLabelText('Corriger le fichier NFO');
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/erreur/i)).toBeInTheDocument();
    });
  });

  it('should call onActionComplete callback after successful action', async () => {
    const onActionComplete = jest.fn();
    mockReleasesApi.nfofix.mockResolvedValue({
      data: { message: 'Success', job_id: 1 },
    });

    renderComponent({ onActionComplete });

    const button = screen.getByLabelText('Corriger le fichier NFO');
    await userEvent.click(button);

    await waitFor(() => {
      expect(onActionComplete).toHaveBeenCalled();
    });
  });
});
