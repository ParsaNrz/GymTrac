import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export function Layout({ children }) {
  const { user, logout, isAuthenticated } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-inner container">
          <Link to="/dashboard" className="logo">GymTrac</Link>
          <nav className="main-nav">
            {isAuthenticated && (
              <>
                <Link to="/dashboard" className="nav-link">Dashboard</Link>
                <Link to="/workout" className="nav-link">Workout</Link>
                <Link to="/calendar" className="nav-link">Calendar</Link>
                <Link to="/exercises" className="nav-link">Exercises</Link>
                <Link to="/settings" className="nav-link">Settings</Link>
                {user?.role === 'admin' && (
                  <Link to="/admin" className="nav-link">Admin</Link>
                )}
                <button className="nav-link btn btn-secondary btn-sm" onClick={handleLogout}>
                  Logout
                </button>
              </>
            )}
          </nav>
          <button className="theme-toggle btn btn-secondary btn-sm" onClick={toggleTheme}>
            {theme === 'dark' ? 'Light' : 'Dark'}
          </button>
        </div>
      </header>
      <main className="app-main container">
        {children}
      </main>
    </div>
  );
}
