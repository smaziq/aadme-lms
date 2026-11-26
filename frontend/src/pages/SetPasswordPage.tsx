import { useState, type FormEvent } from "react";
import { Link, Navigate, useSearchParams } from "react-router-dom";
import { apiRequest } from "../api/client";
import { formatApiError, useAuth, type User } from "../auth/AuthContext";

type SetPasswordResponse = {
  token: string;
  user: User;
};

export function SetPasswordPage() {
  const { user, loading: authLoading, setSession } = useAuth();
  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!authLoading && user) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!inviteToken) {
      setError("Missing invite token. Use the link from your invitation email.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      const data = await apiRequest<SetPasswordResponse>("/api/auth/set-password/", {
        method: "POST",
        body: { token: inviteToken, password },
      });
      setSession(data.token, data.user);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Set your password</h1>
        <p className="auth-subtitle">Complete your AADME Learning account setup</p>
        {!inviteToken && (
          <div className="alert alert-error" role="alert">
            No invite token in the URL. Open the link from your invitation email.
          </div>
        )}
        {error && (
          <div className="alert alert-error" role="alert">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="auth-form">
          <label>
            New password
            <input
              type="password"
              name="password"
              autoComplete="new-password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={submitting || !inviteToken}
            />
          </label>
          <label>
            Confirm password
            <input
              type="password"
              name="confirm"
              autoComplete="new-password"
              required
              minLength={8}
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              disabled={submitting || !inviteToken}
            />
          </label>
          <button
            type="submit"
            className="btn-primary"
            disabled={submitting || authLoading || !inviteToken}
          >
            {submitting ? "Saving…" : "Set password and continue"}
          </button>
        </form>
        <p className="auth-footer">
          Already have a password? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}