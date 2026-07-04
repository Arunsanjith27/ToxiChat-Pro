import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { Shield, RefreshCw, Search, Download, Filter } from 'lucide-react';
import { API_URL } from '../../../services/api';
import AuditTable from './AuditTable';

export default function AuditDashboard() {
  const { user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [filterAction, setFilterAction] = useState('');
  const [filterActor, setFilterActor] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (filterAction) params.append('action', filterAction);
      if (filterActor) params.append('actor', filterActor);
      
      const res = await fetch(`${API_URL}/api/audit?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${user.access_token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setLogs(data);
      } else {
        const data = await res.json();
        setError(data.detail || "Failed to fetch audit logs");
      }
    } catch (err) {
      setError("Network error fetching audit logs.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [filterAction, filterActor, user.access_token]);

  return (
    <div className="flex flex-col h-full bg-black">
      
      {/* Header */}
      <div className="p-6 bg-gray-900 border-b border-white/5 shrink-0 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Shield className="w-6 h-6 text-indigo-500" /> Enterprise Audit Trail
          </h1>
          <p className="text-sm text-gray-400 mt-1">Immutable ledger of critical system actions.</p>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={fetchLogs} 
            className="p-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors border border-white/5"
            title="Refresh Logs"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white text-sm font-medium rounded-lg transition-colors border border-white/5 flex items-center gap-2">
            <Download className="w-4 h-4" /> Export CSV
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 bg-gray-900/50 border-b border-white/5 flex flex-wrap gap-4 shrink-0">
        <div className="flex items-center gap-2 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <select 
            value={filterAction} 
            onChange={(e) => setFilterAction(e.target.value)}
            className="bg-transparent text-sm text-white focus:outline-none"
          >
            <option value="">All Actions</option>
            <option value="LOGIN">Login</option>
            <option value="LOGOUT">Logout</option>
            <option value="INCIDENT_CREATED">Incident Created</option>
            <option value="INCIDENT_ASSIGNED">Incident Assigned</option>
            <option value="INCIDENT_RESOLVED">Incident Resolved</option>
            <option value="STATUS_CHANGED">Status Changed</option>
            <option value="NOTE_ADDED">Note Added</option>
            <option value="COPILOT_USED">Copilot Used</option>
          </select>
        </div>
        
        <div className="flex items-center gap-2 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 flex-1 max-w-sm">
          <Search className="w-4 h-4 text-gray-500" />
          <input 
            type="text"
            placeholder="Filter by Actor Username..."
            value={filterActor}
            onChange={(e) => setFilterActor(e.target.value)}
            className="bg-transparent text-sm text-white focus:outline-none w-full"
          />
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border-b border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Grid */}
      <div className="flex-1 overflow-y-auto relative bg-gray-900/20">
        {loading && logs.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-10">
            <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
          </div>
        ) : null}
        
        <AuditTable logs={logs} />
      </div>

    </div>
  );
}
