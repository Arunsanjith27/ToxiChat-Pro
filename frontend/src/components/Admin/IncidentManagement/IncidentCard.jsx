import React from 'react';
import { AlertTriangle, Clock, User, MessageSquare } from 'lucide-react';
import IncidentStatusBadge from './IncidentStatusBadge';

export default function IncidentCard({ incident, onClick }) {
  const priorityColors = {
    CRITICAL: "text-red-400 bg-red-500/10 border-red-500/30",
    HIGH: "text-orange-400 bg-orange-500/10 border-orange-500/30",
    MEDIUM: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
    LOW: "text-blue-400 bg-blue-500/10 border-blue-500/30"
  };

  const pColor = priorityColors[incident.priority] || priorityColors.LOW;

  return (
    <div 
      onClick={onClick}
      className="p-4 rounded-xl bg-gray-900 border border-white/5 hover:border-white/20 transition-all cursor-pointer flex flex-col gap-3 group"
    >
      <div className="flex justify-between items-start">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${pColor}`}>
            {incident.priority}
          </span>
          <span className="text-xs text-gray-400 font-mono">#{incident.incident_id.split('-')[0]}</span>
        </div>
        <IncidentStatusBadge status={incident.status} />
      </div>

      <div>
        <p className="text-sm text-gray-200 font-medium line-clamp-2">
          {incident.copilot_snapshot?.answer || "Conversation flagged for safety review."}
        </p>
      </div>

      <div className="flex items-center gap-4 text-xs text-gray-500 mt-auto pt-2 border-t border-white/5">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {new Date(incident.created_at).toLocaleDateString()}
        </div>
        <div className="flex items-center gap-1">
          <User className="w-3 h-3" />
          {incident.assigned_to || 'Unassigned'}
        </div>
        <div className="flex items-center gap-1 ml-auto">
          <MessageSquare className="w-3 h-3" />
          {incident.metadata?.message_count || 0}
        </div>
      </div>
    </div>
  );
}
