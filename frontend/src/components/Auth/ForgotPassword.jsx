import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, ArrowLeft, KeyRound } from 'lucide-react';
import { Link } from 'react-router-dom';
import { authApi } from '../../services/api';
import { AuthLayout } from '../Layout/AuthLayout';

export default function ForgotPassword() {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('request');

  const handleRequest = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      const data = await authApi.forgotPassword({ username });
      setSuccess(data.message);
      if (data.token) {
        setResetToken(data.token);
        setStep('reset');
      }
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const handleReset = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authApi.resetPassword({ token: resetToken, new_password: newPassword });
      setSuccess('Password reset successful! You can now sign in.');
      setStep('done');
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <AuthLayout title="Reset Password" subtitle={step === 'request' ? 'Enter your username to receive a reset token' : 'Set your new password'}>
      {step === 'request' && (
        <form onSubmit={handleRequest} className="space-y-4">
          <input
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            required
            className="theme-input w-full rounded-xl px-4 py-3"
          />
          {error && <div className="error-banner">{error}</div>}
          {success && <div className="success-banner">{success}</div>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'Sending...' : 'Get Reset Token'}
          </button>
        </form>
      )}

      {step === 'reset' && (
        <form onSubmit={handleReset} className="space-y-4">
          <input
            placeholder="Reset token"
            value={resetToken}
            onChange={e => setResetToken(e.target.value)}
            required
            className="theme-input w-full rounded-xl px-4 py-3 text-sm"
          />
          <input
            placeholder="New password"
            type="password"
            value={newPassword}
            onChange={e => setNewPassword(e.target.value)}
            required
            minLength={4}
            className="theme-input w-full rounded-xl px-4 py-3"
          />
          {error && <div className="error-banner">{error}</div>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
      )}

      {step === 'done' && (
        <div className="success-banner text-center">{success}</div>
      )}

      <div className="mt-6 text-center">
        <Link to="/login" className="text-sm theme-muted hover:theme-text inline-flex items-center gap-1">
          <ArrowLeft className="w-4 h-4" /> Back to Sign In
        </Link>
      </div>
    </AuthLayout>
  );
}
