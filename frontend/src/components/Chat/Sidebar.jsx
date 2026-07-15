import React from 'react';
import { motion } from 'framer-motion';
import { Users, ShieldAlert, LogOut, Star } from 'lucide-react';
import Avatar from '../Common/Avatar';

const TIER_COLORS = {
  excellent: 'text-emerald-400',
  good: 'text-cyan-400',
  fair: 'text-amber-400',
  poor: 'text-orange-400',
  critical: 'text-red-400',
};

export default function Sidebar({ user, contacts, activeChat, setActiveChat, onLogout, unreadCounts = {} }) {
  return (
    <div className="w-full md:w-80 border-r border-space-border glass-panel rounded-l-3xl flex flex-col overflow-hidden relative z-10 hidden md:flex">
      <div className="p-5 border-b border-white/5 bg-white/5 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 to-cyan-500" />
        <div className="flex items-center gap-3">
          <Avatar user={user} size="lg" />
          <div className="flex-1 overflow-hidden">
            <h2 className="theme-text font-bold truncate text-sm">{user.display_name}</h2>
            <p className="text-xs text-emerald-400 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Online
            </p>
            {user.reputation_score != null && (
              <p className={`text-[10px] flex items-center gap-1 mt-0.5 ${TIER_COLORS[user.reputation_tier] || 'text-gray-400'}`}>
                <Star className="w-3 h-3" /> {user.reputation_score} rep
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="px-4 py-3 border-b border-white/5">
        <p className="text-[11px] theme-muted uppercase tracking-widest font-semibold">Contacts · {contacts.length}</p>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        {contacts.length === 0 ? (
          <div className="text-center py-10 px-4">
            <Users className="text-gray-500 w-7 h-7 mx-auto mb-3" />
            <p className="theme-muted text-sm">No other users yet.</p>
          </div>
        ) : (
          contacts.map((c, i) => {
            const isActive = activeChat?.username === c.username;
            return (
              <motion.div
                key={c.username}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                onClick={() => setActiveChat(c)}
                className={`p-3 rounded-xl cursor-pointer flex items-center gap-3 transition-all ${
                  isActive ? 'bg-emerald-500/10 border border-emerald-500/20' : 'hover:bg-white/5 border border-transparent'
                }`}
              >
                <div className="relative flex-shrink-0">
                  <Avatar user={c} size="md" className={isActive ? 'ring-2 ring-emerald-500' : ''} />
                  {c.is_online && (
                    <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 border-2 border-space-bg rounded-full" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className={`font-medium truncate text-sm ${isActive ? 'theme-text' : 'theme-muted'}`}>
                      {c.display_name || c.username}
                    </h3>
                    {c.is_muted && <ShieldAlert className="w-3 h-3 text-red-400" />}
                  </div>
                  <p className="text-[11px] theme-muted truncate">
                    {c.is_online ? 'Online' : c.last_seen ? `Last seen ${new Date(c.last_seen).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : 'Offline'}
                    {c.reputation_score != null && ` · ${c.reputation_score} rep`}
                  </p>
                </div>
                {(unreadCounts[c.username] || 0) > 0 && (
                  <div className="w-5 h-5 rounded-full bg-emerald-500 text-white text-[10px] font-bold flex items-center justify-center">
                    {unreadCounts[c.username] > 9 ? '9+' : unreadCounts[c.username]}
                  </div>
                )}
              </motion.div>
            );
          })
        )}
      </div>

    </div>
  );
}
