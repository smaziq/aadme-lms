import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function HomePage() {
  const { user, loading, logout } = useAuth();
  const [loggingOut, setLoggingOut] = useState(false);

  if (loading) {
    return (
      <div className="page-center">
        <p className="muted">Loading…</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  async function handleLogout() {
    setLoggingOut(true);
    try {
      await logout();
    } finally {
      setLoggingOut(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="brand">AADME Learning</span>
        <div className="header-actions">
          <span className="user-badge">
            {user.email} · {user.role}
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
      <main className="app-main">
        <h1>Welcome</h1>
        <p className="lead">
          You are signed in as <strong>{user.email}</strong> ({user.role}).
        </p>
        {user.role === "admin" ? (
          <div className="admin-home-links">
            <p className="lead">Admin tools</p>
            <ul>
              <li>
                <Link to="/admin/programs">Manage programs &amp; lessons</Link>
              </li>
              <li>
                <Link to="/admin/enroll">Enroll students</Link>
              </li>
            </ul>
          </div>
        ) : (
          <p className="muted">Your enrolled courses will appear here in a future update.</p>
        )}
      </main>
    </div>
  );
}