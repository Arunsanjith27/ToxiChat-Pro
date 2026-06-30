import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { TrendingUp, ShieldAlert, MessageSquare, BarChart3 } from 'lucide-react';

function StatCard({ icon: Icon, label, value, color, glow }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-${color}-500/10 border border-${color}-500/20 rounded-2xl p-5 flex flex-col ${glow ? `shadow-[0_0_30px_rgba(var(--${color}),0.1)]` : ''}`}
    >
      <div className="flex items-center justify-between mb-3">
        <Icon className={`w-5 h-5 text-${color}-400`} />
      </div>
      <span className={`text-3xl font-bold text-${color}-400 tracking-tight`}>{value}</span>
      <span className={`text-sm font-medium text-${color}-500/70 mt-1 uppercase tracking-wider`}>{label}</span>
    </motion.div>
  );
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900/95 backdrop-blur-md border border-white/10 rounded-xl p-3 shadow-xl">
      <p className="text-gray-400 text-xs mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-sm font-semibold" style={{ color: p.color }}>
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
}

export default function Dashboard({ stats }) {
  const [trendView, setTrendView] = useState('hourly');

  if (!stats) {
    return (
      <div className="flex-1 glass-panel ml-4 rounded-r-3xl flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin" />
          <span className="text-gray-400 text-sm">Loading analytics...</span>
        </div>
      </div>
    );
  }

  const toxRate = (stats.toxicity_rate * 100).toFixed(1);
  const trendData = trendView === 'hourly'
    ? (stats.hourly_trend || []).map(h => ({ name: `${h.hour}:00`, total: h.total, toxic: h.toxic }))
    : (stats.daily_trend || []).map(d => ({ name: d.date?.slice(5), total: d.total, toxic: d.toxic }));

  return (
    <div className="flex-1 flex flex-col relative z-10 glass-panel ml-4 rounded-r-3xl overflow-y-auto shadow-2xl p-8">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-cyan-400 inline-block mb-2">
          Toxicity Dashboard
        </h2>
        <p className="text-gray-400 text-sm">Real-time AI moderation analytics</p>
      </motion.div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0 }}
          className="bg-white/5 border border-white/10 rounded-2xl p-5 flex flex-col">
          <div className="flex items-center justify-between mb-3"><MessageSquare className="w-5 h-5 text-gray-400" /></div>
          <span className="text-3xl font-bold text-white tracking-tight">{stats.total_messages}</span>
          <span className="text-sm font-medium text-gray-400 mt-1 uppercase tracking-wider">Total</span>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
          className="bg-red-500/10 border border-red-500/20 rounded-2xl p-5 flex flex-col shadow-[0_0_30px_rgba(239,68,68,0.1)]">
          <div className="flex items-center justify-between mb-3"><ShieldAlert className="w-5 h-5 text-red-400" /></div>
          <span className="text-3xl font-bold text-red-500 tracking-tight">{stats.toxic_count}</span>
          <span className="text-sm font-medium text-red-400 mt-1 uppercase tracking-wider">Toxic</span>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-5 flex flex-col">
          <div className="flex items-center justify-between mb-3"><MessageSquare className="w-5 h-5 text-emerald-400" /></div>
          <span className="text-3xl font-bold text-emerald-400 tracking-tight">{stats.non_toxic_count}</span>
          <span className="text-sm font-medium text-emerald-500/70 mt-1 uppercase tracking-wider">Safe</span>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="bg-cyan-500/10 border border-cyan-500/20 rounded-2xl p-5 flex flex-col">
          <div className="flex items-center justify-between mb-3"><TrendingUp className="w-5 h-5 text-cyan-400" /></div>
          <span className="text-3xl font-bold text-cyan-400 tracking-tight">{toxRate}%</span>
          <span className="text-sm font-medium text-cyan-500/70 mt-1 uppercase tracking-wider">Rate</span>
        </motion.div>
      </div>

      {(stats.conversation_health_avg != null || stats.escalation_events > 0) && (
        <div className="grid grid-cols-2 gap-4 mb-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="bg-violet-500/10 border border-violet-500/20 rounded-2xl p-5">
            <span className="text-3xl font-bold text-violet-400">{stats.conversation_health_avg?.toFixed?.(0) ?? stats.conversation_health_avg}%</span>
            <span className="text-sm font-medium text-violet-500/70 mt-1 uppercase tracking-wider block">Avg Conversation Health</span>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="bg-orange-500/10 border border-orange-500/20 rounded-2xl p-5">
            <span className="text-3xl font-bold text-orange-400">{stats.escalation_events || 0}</span>
            <span className="text-sm font-medium text-orange-500/70 mt-1 uppercase tracking-wider block">Escalating Conversations</span>
          </motion.div>
        </div>
      )}

      {/* User Stats */}
      {(stats.total_users > 0 || stats.online_users > 0) && (
        <div className="grid grid-cols-2 gap-4 mb-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.18 }}
            className="bg-violet-500/10 border border-violet-500/20 rounded-2xl p-5 flex flex-col">
            <span className="text-3xl font-bold text-violet-400 tracking-tight">{stats.total_users || 0}</span>
            <span className="text-sm font-medium text-violet-500/70 mt-1 uppercase tracking-wider">Total Users</span>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-5 flex flex-col">
            <div className="flex items-center gap-2 mb-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <span className="text-3xl font-bold text-emerald-400 tracking-tight">{stats.online_users || 0}</span>
            <span className="text-sm font-medium text-emerald-500/70 mt-1 uppercase tracking-wider">Online Now</span>
          </motion.div>
        </div>
      )}

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-emerald-400" />
            Toxicity Trend
          </h3>
          <div className="flex gap-1 bg-white/5 rounded-lg p-0.5 border border-white/10">
            {['hourly', 'daily'].map(v => (
              <button
                key={v}
                onClick={() => setTrendView(v)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  trendView === v ? 'bg-emerald-500 text-white shadow' : 'text-gray-400 hover:text-white'
                }`}
              >
                {v.charAt(0).toUpperCase() + v.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <div className="bg-black/20 border border-white/5 rounded-2xl p-4 h-64">
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="toxicGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="total" stroke="#10b981" fill="url(#totalGrad)" strokeWidth={2} name="Total" />
                <Area type="monotone" dataKey="toxic" stroke="#ef4444" fill="url(#toxicGrad)" strokeWidth={2} name="Toxic" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500 text-sm">No data yet</div>
          )}
        </div>
      </motion.div>

      {stats.most_toxic_users?.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="mb-8">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            Most Flagged Users
          </h3>
          <div className="bg-black/20 border border-white/5 rounded-2xl overflow-hidden shadow-inner">
            {stats.most_toxic_users.map((u, i) => (
              <div key={i} className="flex items-center justify-between p-4 border-b border-white/5 last:border-b-0 hover:bg-white/5 transition-colors">
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-500 w-4 font-mono">{i + 1}.</span>
                  <span className="text-white font-medium">{u.username}</span>
                </div>
                <div className="bg-red-500/20 text-red-400 text-xs font-bold px-2 py-1 rounded inline-flex items-center gap-1 border border-red-500/30">
                  {u.toxic_count} flags
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {stats.flagged_messages?.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            Recent Flagged Messages
          </h3>
          <div className="bg-black/20 border border-white/5 rounded-2xl overflow-hidden">
            {stats.flagged_messages.slice(0, 10).map((m, i) => (
              <div key={i} className="p-4 border-b border-white/5 last:border-b-0 hover:bg-white/5 transition-colors">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-emerald-400 text-xs font-semibold">{m.sender}</span>
                  <span className="text-gray-500 text-[10px]">{m.timestamp ? new Date(m.timestamp).toLocaleString() : ''}</span>
                </div>
                <p className="text-gray-300 text-sm truncate">{m.text}</p>
                <span className="text-red-400 text-[10px] font-bold mt-1 inline-block">Score: {(m.score * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
