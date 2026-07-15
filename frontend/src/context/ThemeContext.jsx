import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext(null);
const STORAGE_KEY = 'toxichat_theme';

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem(STORAGE_KEY) || 'system';
  });

  const [actualTheme, setActualTheme] = useState('dark'); // what is actually rendered

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('light', 'dark');

    let newActualTheme = theme;
    if (theme === 'system') {
      newActualTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    root.classList.add(newActualTheme);
    setActualTheme(newActualTheme);
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  // Listen for system theme changes if set to system
  useEffect(() => {
    if (theme !== 'system') return;
    
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e) => {
      const root = document.documentElement;
      root.classList.remove('light', 'dark');
      const newActualTheme = e.matches ? 'dark' : 'light';
      root.classList.add(newActualTheme);
      setActualTheme(newActualTheme);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  // Preserve existing toggleTheme API for backward compatibility
  const toggleTheme = () => setTheme(t => {
    if (t === 'system') return actualTheme === 'dark' ? 'light' : 'dark';
    return t === 'dark' ? 'light' : 'dark';
  });

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme, isDark: actualTheme === 'dark' }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}
