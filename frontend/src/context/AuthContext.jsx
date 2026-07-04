import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

const STORAGE_KEY = 'toxichat_user';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(false);
  // Track whether we have already validated the stored token on initial mount
  const initialValidationDone = useRef(false);
  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;
    return () => { isMounted.current = false; };
  }, []);

  const persist = useCallback((userData) => {
    setUser(userData);
    if (userData) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(userData));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const logout = useCallback(() => persist(null), [persist]);

  // Validate stored token ONCE on initial app mount.
  // This handles page refresh — if the saved token is expired/invalid, log out.
  // It does NOT run again when the user logs in or the token changes during the session.
  useEffect(() => {
    if (initialValidationDone.current) return;
    initialValidationDone.current = true;

    const saved = (() => {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : null;
      } catch {
        return null;
      }
    })();

    if (saved?.access_token) {
      authApi.me(saved.access_token).catch(() => {
        if (isMounted.current) {
          // Token is invalid or expired — clear the session
          persist(null);
        }
      });
    }
  }, []); // Empty deps: runs exactly once on mount

  const login = useCallback(async (credentials) => {
    setLoading(true);
    try {
      const data = await authApi.login(credentials);
      persist(data);
      return data;
    } finally {
      setLoading(false);
    }
  }, [persist]);

  const register = useCallback(async (payload) => {
    setLoading(true);
    try {
      const data = await authApi.register(payload);
      persist(data);
      return data;
    } finally {
      setLoading(false);
    }
  }, [persist]);

  const refreshProfile = useCallback(async () => {
    const token = user?.access_token;
    if (!token) return;
    try {
      const profile = await authApi.me(token);
      if (isMounted.current) {
        persist({ ...user, ...profile, access_token: token });
      }
    } catch {
      // Only log out if the token is genuinely invalid (401), not on network errors
      if (isMounted.current) {
        logout();
      }
    }
  }, [user, persist, logout]);

  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading, refreshProfile, isAdmin, persist }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
