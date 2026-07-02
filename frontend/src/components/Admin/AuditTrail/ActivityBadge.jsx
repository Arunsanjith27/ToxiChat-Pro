import React from 'react';

export default function ActivityBadge({ action }) {
  const styles = {
    // Auth
    LOGIN: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    LOGOUT: "bg-gray-500/10 text-gray-400 border-gray-500/20",
    
    // Incident
    INCIDENT_CREATED: "bg-red-500/10 text-red-400 border-red-500/20",
    INCIDENT_ASSIGNED: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    INCIDENT_RESOLVED: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    STATUS_CHANGED: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    NOTE_ADDED: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    
    // AI
    COPILOT_USED: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  };

  const style = styles[action] || "bg-gray-500/10 text-gray-400 border-gray-500/20";

  return (
    <span className={`px-2 py-1 rounded text-[10px] font-bold font-mono tracking-wider border ${style}`}>
      {action}
    </span>
  );
}
