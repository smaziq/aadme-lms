import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { apiRequest } from "../api/client";

const TOKEN_STORAGE_KEY = "aadme_auth_token";

export type StudentProfile = {
  id: number;
  full_name: string;
  phone: string;
  crm_person_id: string;
};

export type User = {
  id: number;
  email: string;
  role: "admin" | "student";
  student: StudentProfile | null;
};

type LoginResponse = {
  token: string;
  user: User;
};

type AuthContextValue = {
  token: string | null;
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setSession: (token: string, user: User) => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function parseErrorMessage(raw: string): string {
  try {
    const data = JSON.parse(raw) as Record<string, unknown>;
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
      return String(data.non_field_errors[0]);
    }
    const firstKey = Object.keys(data)[0];
    const firstVal = data[firstKey];
    if (Array.isArray(firstVal) && firstVal.length > 0) return String(firstVal[0]);
    if (typeof firstVal === "string") return firstVal;
  } catch {
    /* use raw */
  }
  return raw || "Request failed";
}

export function formatApiError(err: unknown): string {
  if (err instanceof Error) return parseErrorMessage(err.message);
  return "Request failed";
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem(TOKEN_STORAGE_KEY),
  );
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const setSession = useCallback((newToken: string, newUser: User) => {
    localStorage.setItem(TOKEN_STORAGE_KEY, newToken);
    setToken(newToken);
    setUser(newUser);
  }, []);

  const clearSession = useCallback(() => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadMe() {
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const me = await apiRequest<User>("/api/auth/me/", { token });
        if (!cancelled) setUser(me);
      } catch {
        if (!cancelled) clearSession();
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void loadMe();
    return () => {
      cancelled = true;
    };
  }, [token, clearSession]);

  const login = useCallback(
    async (email: string, password: string) => {
      const data = await apiRequest<LoginResponse>("/api/auth/login/", {
        method: "POST",
        body: { email, password },
      });
      setSession(data.token, data.user);
    },
    [setSession],
  );

  const logout = useCallback(async () => {
    if (token) {
      try {
        await apiRequest<void>("/api/auth/logout/", {
          method: "POST",
          token,
        });
      } catch {
        /* clear local session even if server logout fails */
      }
    }
    clearSession();
  }, [token, clearSession]);

  const value = useMemo(
    () => ({ token, user, loading, login, logout, setSession }),
    [token, user, loading, login, logout, setSession],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}