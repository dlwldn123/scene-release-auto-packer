/** Main App component. */

import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { ThemeProvider } from './contexts/ThemeContext';
import { Config } from './pages/Config';
import { Dashboard } from './pages/Dashboard';
import { NewRelease } from './pages/NewRelease';
import { ReleasesList } from './pages/ReleasesList';
import { Roles } from './pages/Roles';
import { Rules } from './pages/Rules';
import { Users } from './pages/Users';
import './styles/App.css';

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
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/releases/new" element={<NewRelease />} />
              <Route path="/releases" element={<ReleasesList />} />
              <Route path="/rules" element={<Rules />} />
              <Route path="/users" element={<Users />} />
              <Route path="/roles" element={<Roles />} />
              <Route path="/config" element={<Config />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
