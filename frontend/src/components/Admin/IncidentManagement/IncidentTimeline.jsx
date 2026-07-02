import React from 'react';
import { Activity, Clock, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function IncidentTimeline({ incident }) {
  const events = [];

  if (incident.created_at) {
    events.push({
      id: 1,
      title: 'Incident Created',
      desc: `Generated from AI flag.`,
      time: incident.created_at,
      icon: <ShieldAlert className="w-4 h-4 text-red-400" />
    });
  }

  if (incident.assigned_to) {
    events.push({
      id: 2,
      title: 'Assigned',
      desc: `Assigned to ${incident.assigned_to}`,
      time: incident.updated_at,
      icon: <Activity className="w-4 h-4 text-yellow-400" />
    });
  }

  if (incident.resolved_at) {
    events.push({
      id: 3,
      title: 'Resolved',
      desc: `Resolved by ${incident.resolved_by}`,
      time: incident.resolved_at,
      icon: <CheckCircle2 className="w-4 h-4 text-emerald-400" />
    });
  }

  events.sort((a, b) => new Date(a.time) - new Date(b.time));

  return (
    <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
      <h4 className="text-sm font-semibold text-gray-200 mb-4 flex items-center gap-2">
        <Clock className="w-4 h-4 text-gray-400" /> Lifecycle Timeline
      </h4>
      <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-700 before:to-transparent">
        {events.map((ev, i) => (
          <div key={ev.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            <div className="flex items-center justify-center w-5 h-5 rounded-full border border-gray-700 bg-gray-900 text-gray-500 group-[.is-active]:text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
              {ev.icon}
            </div>
            <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] p-3 rounded-lg border border-white/5 bg-gray-800 shadow">
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-gray-200 text-xs">{ev.title}</span>
                <span className="text-[10px] text-gray-500 font-mono">{new Date(ev.time).toLocaleTimeString()}</span>
              </div>
              <p className="text-[10px] text-gray-400">{ev.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
