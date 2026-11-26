import { Link, useNavigate } from "react-router-dom";
import { useState, type ReactNode } from "react";
import { useAuth } from "../auth/AuthContext";

export function StudentShell({ children, title }: { children: ReactNode; title: string }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [loggingOut, setLoggingOut] = useState(false);

  async function handleLogout() {
    setLoggingOut(true);
    try {
      await logout();
      navigate("/login");
    } finally {
      setLoggingOut(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="brand">AADME Learning</span>
        <nav className="admin-nav" aria-label="Student">
          <Link to="/">Home</Link>
          <Link to="/courses">My courses</Link>
        </nav>
        <div className="header-actions">
          <span className="user-badge">
            {user?.email} · {user?.role}
          </span>
          <button
            type="button"
            className="btn-secondary"
            onClick={() => void handleLogout()}
            disabled={loggingOut}
          >
            {loggingOut ? "Signing out…" : "Sign out"}
          </button>
        </div>
      </header>
      <main className="app-main admin-main">
        <h1>{title}</h1>
        {children}
      </main>
    </div>
  );
}