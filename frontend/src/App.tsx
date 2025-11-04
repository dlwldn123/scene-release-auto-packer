/** Main App component. */

import { lazy, Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { ThemeProvider } from './contexts/ThemeContext';
import './styles/App.css';

// Lazy load routes for code splitting
const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const NewRelease = lazy(() => import('./pages/NewRelease').then(m => ({ default: m.NewRelease })));
const ReleasesList = lazy(() => import('./pages/ReleasesList').then(m => ({ default: m.ReleasesList })));
const ReleaseEdit = lazy(() => import('./pages/ReleaseEdit').then(m => ({ default: m.ReleaseEdit })));
const ReleaseDetail = lazy(() => import('./pages/ReleaseDetail').then(m => ({ default: m.ReleaseDetail })));
const Rules = lazy(() => import('./pages/Rules').then(m => ({ default: m.Rules })));
const Users = lazy(() => import('./pages/Users').then(m => ({ default: m.Users })));
const Roles = lazy(() => import('./pages/Roles').then(m => ({ default: m.Roles })));
const Config = lazy(() => import('./pages/Config').then(m => ({ default: m.Config })));

/**
 * Loading fallback component.
 */
function LoadingFallback() {
  return (
    <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">Chargement...</span>
      </div>
    </div>
  );
}

/**
 * Main App component with routing.
 */
function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="app-shell">
          <Navbar />
          <main className="container-fluid">
            <Suspense fallback={<LoadingFallback />}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/releases/new" element={<NewRelease />} />
                <Route path="/releases" element={<ReleasesList />} />
                <Route path="/releases/:id/edit" element={<ReleaseEdit />} />
                <Route path="/releases/:id" element={<ReleaseDetail />} />
                <Route path="/rules" element={<Rules />} />
                <Route path="/users" element={<Users />} />
                <Route path="/roles" element={<Roles />} />
                <Route path="/config" element={<Config />} />
              </Routes>
            </Suspense>
          </main>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
