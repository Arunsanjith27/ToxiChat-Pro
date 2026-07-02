import React from 'react';
import ActivityBadge from './ActivityBadge';
import { Fingerprint, User, FileText, Database } from 'lucide-react';

export default function AuditTable({ logs }) {
  if (!logs || logs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-500">
        <Database className="w-12 h-12 mb-4 opacity-50" />
        <p>No audit logs found.</p>
      </div>
    );
  }

  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full text-left text-sm text-gray-300">
        <thead className="text-xs text-gray-500 uppercase bg-gray-900/50 border-b border-white/10 sticky top-0">
          <tr>
            <th className="px-4 py-3">Timestamp</th>
            <th className="px-4 py-3">Actor</th>
            <th className="px-4 py-3">Action</th>
            <th className="px-4 py-3">Resource</th>
            <th className="px-4 py-3">Description</th>
            <th className="px-4 py-3 text-right">Audit ID</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {logs.map((log) => (
            <tr key={log.audit_id} className="hover:bg-white/[0.02] transition-colors">
              <td className="px-4 py-3 whitespace-nowrap text-gray-400 font-mono text-xs">
                {new Date(log.timestamp).toLocaleString()}
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                <div className="flex items-center gap-2">
                  <User className="w-3 h-3 text-gray-500" />
                  <span className="font-medium text-white">{log.actor_username}</span>
                </div>
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                <ActivityBadge action={log.action} />
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                <div className="flex items-center gap-1 text-gray-400 text-xs">
                  <FileText className="w-3 h-3" />
                  {log.resource_type}: <span className="font-mono">{log.resource_id.split('-')[0]}</span>
                </div>
              </td>
              <td className="px-4 py-3 text-gray-300 max-w-xs truncate">
                {log.description}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-right">
                <div className="flex items-center justify-end gap-1 text-gray-600 font-mono text-[10px]">
                  <Fingerprint className="w-3 h-3" />
                  {log.audit_id.split('-')[0]}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
