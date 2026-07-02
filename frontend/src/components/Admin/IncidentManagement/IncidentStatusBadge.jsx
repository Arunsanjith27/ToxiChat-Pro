import React from 'react';

export default function IncidentStatusBadge({ status }) {
  const styles = {
    OPEN: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    UNDER_INVESTIGATION: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    WAITING_FOR_REVIEW: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    RESOLVED: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    CLOSED: "bg-gray-500/10 text-gray-400 border-gray-500/20",
    ARCHIVED: "bg-zinc-800 text-zinc-400 border-zinc-700",
  };

  const style = styles[status] || "bg-gray-500/10 text-gray-400 border-gray-500/20";
  const label = status.replace(/_/g, ' ');

  return (
    <span className={`px-2 py-1 rounded-md text-[10px] font-bold tracking-wider uppercase border ${style}`}>
      {label}
    </span>
  );
}
