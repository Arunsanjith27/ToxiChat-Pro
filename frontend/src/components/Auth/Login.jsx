import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, UserPlus, LogIn } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { AuthLayout } from '../Layout/AuthLayout';

export default function Login() {
  const { login, register, loading } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await register({ username, password, display_name: displayName || username });
      } else {
        await login({ username, password });
      }
      navigate('/chat');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <AuthLayout title="ToxiChat" subtitle="AI-Powered Safe Messaging Platform">
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
          className="theme-input w-full rounded-xl px-4 py-3"
        />

        {isRegister && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
            <input
              placeholder="Display Name (optional)"
              value={displayName}
              onChange={e => setDisplayName(e.target.value)}
              className="theme-input w-full rounded-xl px-4 py-3"
            />
          </motion.div>
        )}

        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
          className="theme-input w-full rounded-xl px-4 py-3"
        />

        {error && <div className="error-banner">{error}</div>}

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          type="submit"
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : isRegister ? (
            <><UserPlus className="w-5 h-5" /> Create Account</>
          ) : (
            <><LogIn className="w-5 h-5" /> Sign In</>
          )}
        </motion.button>
      </form>

      <div className="mt-6 flex flex-col items-center gap-2">
        <button
          onClick={() => { setIsRegister(!isRegister); setError(''); }}
          className="text-sm theme-muted hover:theme-text transition-colors"
        >
          {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Register"}
        </button>
        {!isRegister && (
          <Link to="/forgot-password" className="text-sm text-emerald-400 hover:text-emerald-300">
            Forgot password?
          </Link>
        )}
      </div>
    </AuthLayout>
  );
}
