/** Navigation bar component. */

import { Link, useLocation } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';

/**
 * Navigation bar component.
 */
export function Navbar() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/releases/new', label: 'Nouvelle Release' },
    { path: '/releases', label: 'Liste Releases' },
    { path: '/rules', label: 'Rules' },
    { path: '/users', label: 'Utilisateurs' },
    { path: '/roles', label: 'Rôles' },
    { path: '/config', label: 'Configurations' },
  ];

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
      <div className="container-fluid">
        <Link className="navbar-brand" to="/">
          eBook Scene Packer v2
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            {navItems.map((item) => (
              <li key={item.path} className="nav-item">
                <Link
                  className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                  to={item.path}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
          <div className="d-flex">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  );
}
