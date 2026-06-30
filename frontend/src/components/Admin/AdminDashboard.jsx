import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, UserX, UserCheck, Shield, RefreshCw, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { adminApi } from '../../services/api';
import ThemeToggle from '../Layout/ThemeToggle';
import Avatar from '../Common/Avatar';

export default function AdminDashboard() {
  const { user } = useAuth();
  const [flagged, setFlagged] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [f, u] = await Promise.all([
        adminApi.flagged(user.access_token),
        adminApi.users(user.access_token),
      ]);
      setFlagged(Array.isArray(f) ? f : []);
      setUsers(Array.isArray(u) ? u : []);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [user.access_token]);

  const runAction = async (username, action) => {
    try {
      await adminApi.action({ username, action }, user.access_token);
      setActionMsg(`${action} applied to ${username}`);
      await load();
      setTimeout(() => setActionMsg(''), 3000);
    } catch (err) {
      setActionMsg(err.message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold theme-text flex items-center gap-2">
            <Shield className="w-8 h-8 text-emerald-400" /> Admin Moderation
          </h1>
          <p className="theme-muted text-sm mt-1">Manage flagged content and user reputation</p>
        </div>
        <div className="flex gap-2">
          <button onClick={load} className="btn-secondary p-2 rounded-xl"><RefreshCw className="w-4 h-4" /></button>
          <ThemeToggle />
          <Link to="/chat" className="btn-secondary text-sm px-4 py-2 rounded-xl inline-flex items-center gap-1">
            <ArrowLeft className="w-4 h-4" /> Chat
          </Link>
        </div>
      </div>

      {actionMsg && <div className="success-banner mb-4">{actionMsg}</div>}

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="glass-panel rounded-2xl p-6">
          <h2 className="text-lg font-semibold theme-text mb-4 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-400" /> Flagged Messages ({flagged.length})
          </h2>
          <div className="space-y-3 max-h-[500px] overflow-y-auto">
            {flagged.length === 0 ? (
              <p className="theme-muted text-sm">No flagged messages</p>
            ) : flagged.map((m, i) => (
              <div key={m.id || i} className="p-4 rounded-xl bg-black/10 border border-white/5">
                <div className="flex justify-between mb-1">
                  <span className="text-emerald-400 text-sm font-medium">{m.sender}</span>
                  <span className="text-red-400 text-xs font-bold">{(m.toxicity_score * 100).toFixed(0)}%</span>
                </div>
                <p className="theme-text text-sm truncate">{m.text}</p>
                <p className="theme-muted text-[10px] mt-1">{m.timestamp ? new Date(m.timestamp).toLocaleString() : ''}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-6">
          <h2 className="text-lg font-semibold theme-text mb-4">User Management ({users.length})</h2>
          <div className="space-y-2 max-h-[500px] overflow-y-auto">
            {users.map(u => (
              <div key={u.username} className="p-3 rounded-xl bg-black/10 border border-white/5 flex items-center gap-3">
                <Avatar user={u} size="sm" />
                <div className="flex-1 min-w-0">
                  <p className="theme-text text-sm font-medium truncate">{u.display_name || u.username}</p>
                  <p className="theme-muted text-[11px]">
                    Rep: {u.reputation_score} · Warnings: {u.warnings_count}
                    {u.is_muted && ' · MUTED'}
                    {u.role === 'admin' && ' · ADMIN'}
                  </p>
                </div>
                <div className="flex gap-1 flex-shrink-0">
                  {u.is_muted && (
                    <button onClick={() => runAction(u.username, 'unmute')} title="Unmute"
                      className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20">
                      <UserCheck className="w-3.5 h-3.5" />
                    </button>
                  )}
                  <button onClick={() => runAction(u.username, 'reset_warnings')} title="Reset warnings"
                    className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400 hover:bg-amber-500/20">
                    <RefreshCw className="w-3.5 h-3.5" />
                  </button>
                  {u.role !== 'admin' ? (
                    <button onClick={() => runAction(u.username, 'promote_admin')} title="Promote"
                      className="p-1.5 rounded-lg bg-violet-500/10 text-violet-400 hover:bg-violet-500/20">
                      <Shield className="w-3.5 h-3.5" />
                    </button>
                  ) : u.username !== user.username && (
                    <button onClick={() => runAction(u.username, 'demote_admin')} title="Demote"
                      className="p-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20">
                      <UserX className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
