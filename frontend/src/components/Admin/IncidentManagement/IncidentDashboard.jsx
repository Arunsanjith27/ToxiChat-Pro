import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { API_URL } from '../../../services/api';
import { Search, ShieldAlert, Plus, RefreshCw, FolderOpen, Archive, CheckCircle } from 'lucide-react';
import IncidentCard from './IncidentCard';
import IncidentDetails from './IncidentDetails';

export default function IncidentDashboard() {
  const { user } = useAuth();
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIncident, setSelectedIncident] = useState(null);
  
  const [filterStatus, setFilterStatus] = useState('');
  const [filterPriority, setFilterPriority] = useState('');

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterStatus) params.append('status', filterStatus);
      if (filterPriority) params.append('priority', filterPriority);
      
      const res = await fetch(`${API_URL}/api/incidents?${params.toString()}`, {
        headers: { 'Authorization': `Bearer ${user.access_token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setIncidents(data);
      }
      
      if (selectedIncident) {
        const dRes = await fetch(`${API_URL}/api/incidents/${selectedIncident.incident_id}`, {
          headers: { 'Authorization': `Bearer ${user.access_token}` }
        });
        if (dRes.ok) {
          const detail = await dRes.json();
          setSelectedIncident(detail);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [filterStatus, filterPriority, user.access_token]);

  // If viewing an incident, render the detail view
  if (selectedIncident) {
    return (
      <IncidentDetails 
        incident={selectedIncident} 
        token={user.access_token}
        onBack={() => { setSelectedIncident(null); fetchIncidents(); }}
        onUpdate={fetchIncidents}
      />
    );
  }

  // Dashboard View
  return (
    <div className="flex flex-col h-full bg-black">
      
      {/* Header */}
      <div className="p-6 bg-gray-900 border-b border-white/5 shrink-0 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-red-500" /> Moderation Operations (ModOps)
          </h1>
          <p className="text-sm text-gray-400 mt-1">Manage AI-flagged safety incidents.</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={fetchIncidents} className="p-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors border border-white/5">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 bg-gray-900 border-b border-white/5 flex gap-4 shrink-0">
        <select 
          value={filterStatus} 
          onChange={(e) => setFilterStatus(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none"
        >
          <option value="">All Statuses</option>
          <option value="OPEN">Open</option>
          <option value="UNDER_INVESTIGATION">Under Investigation</option>
          <option value="WAITING_FOR_REVIEW">Waiting for Review</option>
          <option value="RESOLVED">Resolved</option>
          <option value="ARCHIVED">Archived</option>
        </select>
        
        <select 
          value={filterPriority} 
          onChange={(e) => setFilterPriority(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none"
        >
          <option value="">All Priorities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      {/* Grid */}
      <div className="flex-1 overflow-y-auto p-6">
        {loading && incidents.length === 0 ? (
          <div className="flex items-center justify-center h-40">
            <RefreshCw className="w-6 h-6 text-indigo-400 animate-spin" />
          </div>
        ) : incidents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-60 bg-gray-900 border border-white/5 rounded-xl">
             <FolderOpen className="w-12 h-12 text-gray-600 mb-2" />
             <p className="text-gray-400 text-sm">No incidents found matching your criteria.</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {incidents.map(inc => (
              <IncidentCard 
                key={inc.incident_id} 
                incident={inc} 
                onClick={() => setSelectedIncident(inc)} 
              />
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
