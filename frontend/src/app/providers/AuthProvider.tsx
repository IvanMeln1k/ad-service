import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { saveAuth, loadAuth, clearAuth, type StoredAuth } from '@/shared/lib/tokens';
import { logoutUser } from '@/entities/user/api';
import type { AuthResponse } from '@/entities/user/model';

interface AuthContextValue {
  auth: StoredAuth | null;
  isAuthenticated: boolean;
  handleAuthSuccess: (data: AuthResponse) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<StoredAuth | null>(loadAuth);

  const handleAuthSuccess = useCallback((data: AuthResponse) => {
    const stored: StoredAuth = {
      user_id: data.user_id,
      access_token: data.access_token,
      refresh_token: data.refresh_token.token,
    };
    saveAuth(stored);
    setAuth(stored);
  }, []);

  const logout = useCallback(async () => {
    if (auth) {
      try {
        await logoutUser({ user_id: auth.user_id, refresh_token: auth.refresh_token });
      } catch {
        // ignore — clear local state anyway
      }
    }
    clearAuth();
    setAuth(null);
  }, [auth]);

  return (
    <AuthContext.Provider value={{ auth, isAuthenticated: auth !== null, handleAuthSuccess, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
