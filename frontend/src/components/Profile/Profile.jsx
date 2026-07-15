import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Camera, Save, ArrowLeft, Star } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { profileApi, avatarUrl } from '../../services/api';
import { AdminLayout } from '../Layout/AdminLayout';
import Avatar from '../Common/Avatar';

const TIER_COLORS = {
  excellent: 'text-emerald-400',
  good: 'text-cyan-400',
  fair: 'text-amber-400',
  poor: 'text-orange-400',
  critical: 'text-red-400',
};

export default function Profile() {
  const { user, refreshProfile, persist } = useAuth();
  const [displayName, setDisplayName] = useState(user?.display_name || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileRef = useRef(null);

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const updated = await profileApi.update({ display_name: displayName, bio }, user.access_token);
      persist({ ...user, ...updated, access_token: user.access_token });
      setSuccess('Profile updated');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const handleAvatar = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const { avatar_url } = await profileApi.uploadAvatar(file, user.access_token);
      persist({ ...user, avatar_url, access_token: user.access_token });
      await refreshProfile();
      setSuccess('Avatar updated');
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const tier = user?.reputation_tier || 'excellent';
  const score = user?.reputation_score ?? 100;

  return (
    <AdminLayout maxWidth="lg">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="glass-panel w-full p-8 rounded-3xl mt-10">
        <h1 className="text-2xl font-bold theme-text mb-6">Profile Settings</h1>

        <div className="flex flex-col items-center mb-8">
          <div className="relative group">
            <Avatar user={user} size="xl" />
            <button
              onClick={() => fileRef.current?.click()}
              className="absolute inset-0 rounded-2xl bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity"
            >
              <Camera className="w-6 h-6 text-white" />
            </button>
            <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleAvatar} />
          </div>
          <p className="theme-muted text-sm mt-3">@{user?.username}</p>
          <div className="flex items-center gap-2 mt-2">
            <Star className={`w-4 h-4 ${TIER_COLORS[tier]}`} />
            <span className={`text-sm font-semibold ${TIER_COLORS[tier]}`}>
              {score} · {tier}
            </span>
          </div>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="text-xs theme-muted uppercase tracking-wider">Display Name</label>
            <input value={displayName} onChange={e => setDisplayName(e.target.value)}
              className="theme-input w-full rounded-xl px-4 py-3 mt-1" />
          </div>
          <div>
            <label className="text-xs theme-muted uppercase tracking-wider">Bio</label>
            <textarea value={bio} onChange={e => setBio(e.target.value)} maxLength={200}
              rows={3} className="theme-input w-full rounded-xl px-4 py-3 mt-1 resize-none" />
          </div>
          {error && <div className="error-banner">{error}</div>}
          {success && <div className="success-banner">{success}</div>}
          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
            <Save className="w-4 h-4" /> {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </motion.div>
    </AdminLayout>
  );
}
