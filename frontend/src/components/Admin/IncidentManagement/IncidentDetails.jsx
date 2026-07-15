import React from 'react';
import { ArrowLeft, ShieldAlert, Cpu, Activity, Download, CheckCircle } from 'lucide-react';
import { API_URL } from '../../../services/api';
import IncidentStatusBadge from './IncidentStatusBadge';
import IncidentNotes from './IncidentNotes';
import IncidentTimeline from './IncidentTimeline';
import IncidentAssignment from './IncidentAssignment';
import ConversationSummaryPanel from '../../Dashboard/ConversationSummaryPanel';

export default function IncidentDetails({ incident, token, onBack, onUpdate }) {
  if (!incident) return null;

  const handleStatusChange = async (newStatus) => {
    try {
      const res = await fetch(`${API_URL}/api/incidents/${incident.incident_id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok && onUpdate) onUpdate();
    } catch (err) {
      console.error(err);
    }
  };

  const handleResolve = async () => {
    try {
      const res = await fetch(`${API_URL}/api/incidents/${incident.incident_id}/resolve`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok && onUpdate) onUpdate();
    } catch (err) {
      console.error(err);
    }
  };

  const handleArchive = async () => {
    try {
      const res = await fetch(`${API_URL}/api/incidents/${incident.incident_id}/archive`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok && onUpdate) onUpdate();
    } catch (err) {
      console.error(err);
    }
  };

  const pColor = {
    CRITICAL: "text-red-400 bg-red-500/10 border-red-500/30",
    HIGH: "text-orange-400 bg-orange-500/10 border-orange-500/30",
    MEDIUM: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
    LOW: "text-blue-400 bg-blue-500/10 border-blue-500/30"
  }[incident.priority] || "text-gray-400 bg-gray-500/10 border-gray-500/30";

  return (
    <div className="flex flex-col h-full bg-black">
      
      {/* Header Bar */}
      <div className="flex items-center justify-between p-4 bg-gray-900 border-b border-white/10 shrink-0">
        <div className="flex items-center gap-4">
          <button onClick={onBack} className="p-2 hover:bg-white/5 rounded-lg text-gray-400 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-bold text-white font-mono">INCIDENT #{incident.incident_id.split('-')[0]}</h2>
              <IncidentStatusBadge status={incident.status} />
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold border uppercase ${pColor}`}>
                {incident.priority} PRIORITY
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">Conversation: {incident.conversation_id}</p>
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex gap-2">
          {incident.status !== 'RESOLVED' && incident.status !== 'ARCHIVED' && (
            <button onClick={handleResolve} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
              <CheckCircle className="w-4 h-4" /> Resolve
            </button>
          )}
          {incident.status === 'RESOLVED' && (
            <button onClick={handleArchive} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors">
              Archive Incident
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-3 gap-6">
          
          {/* Main Content Column */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Copilot Forensic Summary (Immutable) */}
            <div className="bg-gray-900 border border-white/5 rounded-xl overflow-hidden">
              <div className="bg-indigo-900/40 p-3 border-b border-white/5 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold text-white">AI Copilot Incident Brief</h3>
              </div>
              <div className="p-4">
                <p className="text-sm text-gray-200 leading-relaxed">
                  {incident.copilot_snapshot?.answer || "No AI brief available."}
                </p>
                {incident.copilot_snapshot?.recommendations?.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-white/5">
                    <p className="text-[10px] font-bold text-gray-400 uppercase mb-2">Recommended Actions</p>
                    <div className="flex flex-wrap gap-2">
                      {incident.copilot_snapshot.recommendations.map((r, i) => (
                         <span key={i} className="px-2 py-1 bg-white/5 border border-white/10 rounded text-xs text-gray-300">
                           {r.action}
                         </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Evidence / Analytics Snapshot */}
            <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
               <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                 <Activity className="w-4 h-4 text-emerald-400" /> Evidence Snapshot
               </h3>
               <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                 <div className="p-3 bg-black/40 rounded-lg border border-white/5">
                   <p className="text-[10px] text-gray-500 font-bold uppercase">Messages</p>
                   <p className="text-lg font-mono text-white">{incident.metadata?.message_count ?? 'N/A'}</p>
                 </div>
                 <div className="p-3 bg-black/40 rounded-lg border border-white/5">
                   <p className="text-[10px] text-gray-500 font-bold uppercase">Health</p>
                   <p className="text-lg font-mono text-white">{incident.analytics_snapshot?.conversation_health_score ?? 'N/A'}/100</p>
                 </div>
                 <div className="p-3 bg-black/40 rounded-lg border border-white/5">
                   <p className="text-[10px] text-gray-500 font-bold uppercase">Risk Trend</p>
                   <p className="text-lg font-bold text-white">{incident.prediction_snapshot?.prediction?.trend ?? 'UNKNOWN'}</p>
                 </div>
                 <div className="p-3 bg-black/40 rounded-lg border border-white/5">
                   <p className="text-[10px] text-gray-500 font-bold uppercase">State</p>
                   <p className="text-lg font-bold text-red-400">{incident.analytics_snapshot?.conversation_state ?? 'UNKNOWN'}</p>
                 </div>
               </div>
            </div>

            {/* In a real app we'd load the ConversationSummaryPanel here with historical mode */}
            {/* We will just reuse the standard panel for the demo, but pass the ID */}
            <div className="bg-gray-900 border border-white/5 rounded-xl overflow-hidden">
               <div className="p-3 border-b border-white/5">
                 <h3 className="text-sm font-bold text-white">Live Conversation View</h3>
               </div>
               <div className="p-4">
                 <ConversationSummaryPanel conversationId={incident.conversation_id} />
               </div>
            </div>

          </div>

          {/* Sidebar Column */}
          <div className="space-y-6">
            <IncidentAssignment 
              incidentId={incident.incident_id} 
              currentAssignee={incident.assigned_to} 
              token={token} 
              onUpdate={onUpdate}
            />
            
            <IncidentTimeline incident={incident} />
            
            <div className="h-[400px]">
              <IncidentNotes incidentId={incident.incident_id} token={token} />
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}
