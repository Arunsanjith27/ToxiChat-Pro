import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, UserX, UserCheck, Shield, RefreshCw, ArrowLeft, Activity, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { adminApi } from '../../services/api';
import ThemeToggle from '../Layout/ThemeToggle';
import Avatar from '../Common/Avatar';
import ConversationSummaryPanel from '../Dashboard/ConversationSummaryPanel';
import ImageEvidenceViewer from './ImageEvidenceViewer';
import AudioEvidenceViewer from './AudioEvidenceViewer';
import ConversationPredictionCard from './ConversationPredictionCard';
import ModeratorCopilotPanel from './ModeratorCopilotPanel';
import IncidentDashboard from './IncidentManagement/IncidentDashboard';
import AuditDashboard from './AuditTrail/AuditDashboard';
import ComplianceDashboard from './ComplianceReports/ComplianceDashboard';
import ImageModerationTab from './ImageModerationTab';

export default function AdminDashboard() {
  const { user } = useAuth();
  const [flagged, setFlagged] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState('');

  const [highRisk, setHighRisk] = useState([]);
  const [selectedAnalytics, setSelectedAnalytics] = useState(null);
  
  const [activeTab, setActiveTab] = useState('modops'); // Default to new ModOps view

  const load = async () => {
    setLoading(true);
    try {
      const [f, u, hr] = await Promise.all([
        adminApi.flagged(user.access_token),
        adminApi.users(user.access_token),
        adminApi.highRiskConversations(user.access_token).catch(() => []),
      ]);
      setFlagged(Array.isArray(f) ? f : []);
      setUsers(Array.isArray(u) ? u : []);
      setHighRisk(Array.isArray(hr) ? hr : []);
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
            <Shield className="w-8 h-8 text-emerald-400" /> Admin & ModOps
          </h1>
          <p className="theme-muted text-sm mt-1">Manage flagged content and incidents</p>
        </div>
        <div className="flex gap-2">
          <button onClick={load} className="btn-secondary p-2 rounded-xl"><RefreshCw className="w-4 h-4" /></button>
          <ThemeToggle />
          <Link to="/chat" className="btn-secondary text-sm px-4 py-2 rounded-xl inline-flex items-center gap-1">
            <ArrowLeft className="w-4 h-4" /> Chat
          </Link>
        </div>
      </div>

      <div className="flex gap-2 mb-6 border-b border-white/5 pb-2">
        <button 
          onClick={() => setActiveTab('modops')}
          className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${activeTab === 'modops' ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:bg-white/5'}`}
        >
          Incident Management (ModOps)
        </button>
        <button 
          onClick={() => setActiveTab('classic')}
          className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${activeTab === 'classic' ? 'bg-emerald-600 text-white' : 'text-gray-400 hover:bg-white/5'}`}
        >
          Raw AI Telemetry (Classic)
        </button>
        <button 
          onClick={() => setActiveTab('audit')}
          className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${activeTab === 'audit' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:bg-white/5'}`}
        >
          Audit Trail (Compliance)
        </button>
        <button 
          onClick={() => setActiveTab('reports')}
          className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${activeTab === 'reports' ? 'bg-emerald-600 text-white' : 'text-gray-400 hover:bg-white/5'}`}
        >
          Report Generator
        </button>
        <button 
          onClick={() => setActiveTab('image-mod')}
          className={`px-4 py-2 rounded-lg text-sm font-bold transition-colors ${activeTab === 'image-mod' ? 'bg-pink-600 text-white' : 'text-gray-400 hover:bg-white/5'}`}
        >
          Image Moderation
        </button>
      </div>

      {actionMsg && <div className="success-banner mb-4">{actionMsg}</div>}

      {activeTab === 'reports' && (
        <div className="h-[800px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
          <ComplianceDashboard />
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="h-[800px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
          <AuditDashboard />
        </div>
      )}

      {activeTab === 'image-mod' && (
        <div className="h-[800px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl p-6 bg-gray-900/50">
          <ImageModerationTab />
        </div>
      )}

      {activeTab === 'modops' && (
        <div className="h-[800px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl">
          <IncidentDashboard />
        </div>
      )}

      {activeTab === 'classic' && (
        <>
          {highRisk.length === 0 ? (
            <div className="glass-panel rounded-2xl p-6 mb-6 flex flex-col items-center justify-center h-40">
              <Activity className="w-8 h-8 text-gray-500 mb-2 opacity-50" />
              <p className="text-gray-400 text-sm">No telemetry available.</p>
            </div>
          ) : (
        <div className="glass-panel rounded-2xl p-6 mb-6 border border-red-500/20">
          <h2 className="text-lg font-semibold theme-text mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-red-400" /> High-Risk Radar (Active Conversations)
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {highRisk.map((conv, i) => (
              <div key={i} className="p-4 rounded-xl bg-red-500/5 border border-red-500/10 flex justify-between items-center">
                <div>
                  <h3 className="text-sm font-bold theme-text">{conv.target}</h3>
                  <p className="text-xs text-red-400 font-medium">State: {conv.analytics.conversation_state} | Risk Score: {conv.analytics.average_risk_score}</p>
                  <p className="text-[10px] theme-muted mt-1">
                    Toxicity: {(conv.analytics.overall_toxicity_ratio * 100).toFixed(0)}% | PII: {conv.analytics.pii_instances} | Health: {conv.analytics.conversation_health_score}/100
                  </p>
                </div>
                <button
                  onClick={() => setSelectedAnalytics(conv)}
                  className="p-2 bg-red-500/10 hover:bg-red-500/20 rounded-lg text-red-400 transition-colors flex items-center gap-2 text-xs"
                >
                  <Eye className="w-4 h-4" /> View Deep-Dive
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* NEW: Image Moderation Inspector */}
      <div className="mb-6 grid lg:grid-cols-2 gap-6">
        <ImageEvidenceViewer />
        <AudioEvidenceViewer />
      </div>

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

      {selectedAnalytics && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-gray-900 border border-white/10 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden shadow-2xl">
            <div className="p-4 border-b border-white/10 flex justify-between items-center bg-gray-800/50">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-red-400" /> Conversation Intelligence: {selectedAnalytics.target}
              </h2>
              <button onClick={() => setSelectedAnalytics(null)} className="p-2 hover:bg-white/10 rounded-lg text-gray-400 transition-colors">
                <UserX className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                  <p className="text-xs text-gray-400 mb-1">State</p>
                  <p className={`text-xl font-bold ${selectedAnalytics.analytics.conversation_state === 'CRITICAL' ? 'text-red-400' : 'text-amber-400'}`}>
                    {selectedAnalytics.analytics.conversation_state}
                  </p>
                </div>
                <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                  <p className="text-xs text-gray-400 mb-1">Health Score</p>
                  <p className="text-xl font-bold text-white">{selectedAnalytics.analytics.conversation_health_score}/100</p>
                </div>
                <div className="bg-black/20 p-4 rounded-xl border border-white/5">
                  <p className="text-xs text-gray-400 mb-1">Avg Risk</p>
                  <p className="text-xl font-bold text-white">{selectedAnalytics.analytics.average_risk_score}</p>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-semibold text-gray-300 mb-2 border-b border-white/5 pb-2">Critical Events ({selectedAnalytics.analytics.critical_events?.length || 0})</h3>
                <div className="space-y-2">
                  {selectedAnalytics.analytics.critical_events?.map((ev, i) => (
                    <div key={i} className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-sm">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-red-300 font-bold">{ev.sender}</span>
                        <span className="text-red-400 font-mono">Risk: {ev.risk_score}</span>
                      </div>
                      <ul className="list-disc list-inside text-red-200/80 text-xs">
                        {ev.reasons.map((r, j) => <li key={j}>{r}</li>)}
                      </ul>
                    </div>
                  ))}
                  {(!selectedAnalytics.analytics.critical_events || selectedAnalytics.analytics.critical_events.length === 0) && (
                    <p className="text-xs text-gray-500 italic">No critical events detected.</p>
                  )}
                </div>
              </div>

              {/* Add the new Conversation Intelligence Summary Panel here */}
              <div className="mt-6 space-y-6">
                <ConversationPredictionCard conversationId={selectedAnalytics.target} />
                <div className="grid lg:grid-cols-2 gap-6">
                  <ConversationSummaryPanel conversationId={selectedAnalytics.target} />
                  <ModeratorCopilotPanel conversationId={selectedAnalytics.target} />
                </div>
              </div>
            </div>
            <div className="p-4 border-t border-white/10 bg-gray-800/50 flex justify-end">
              <button onClick={() => setSelectedAnalytics(null)} className="btn-secondary px-6 py-2 rounded-xl text-sm font-medium">Close Report</button>
            </div>
          </div>
        </div>
      )}
      </>
      )}
    </div>
  );
}
