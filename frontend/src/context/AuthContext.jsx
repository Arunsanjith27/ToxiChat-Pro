import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
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

  const persist = useCallback((userData) => {
    setUser(userData);
    if (userData) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(userData));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

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

  const logout = useCallback(() => persist(null), [persist]);

  const refreshProfile = useCallback(async () => {
    if (!user?.access_token) return;
    try {
      const profile = await authApi.me(user.access_token);
      persist({ ...user, ...profile, access_token: user.access_token });
    } catch {
      logout();
    }
  }, [user, persist, logout]);

  useEffect(() => {
    if (user?.access_token) {
      authApi.me(user.access_token).catch(() => logout());
    }
  }, [user?.access_token, logout]);

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
