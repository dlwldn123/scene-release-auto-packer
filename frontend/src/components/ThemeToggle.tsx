/** Theme toggle component. */

import { useTheme } from '../contexts/ThemeContext';

/**
 * Theme toggle button component.
 */
export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <button
      type="button"
      className="btn btn-outline-secondary"
      onClick={toggleTheme}
      aria-label={`Switch to ${resolvedTheme === 'light' ? 'dark' : 'light'} mode`}
    >
      {resolvedTheme === 'light' ? '🌙' : '☀️'}
    </button>
  );
}
