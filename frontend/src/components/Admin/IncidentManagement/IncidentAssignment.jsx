import React, { useState } from 'react';
import { UserPlus, UserCheck, AlertTriangle } from 'lucide-react';
import { API_URL } from '../../../services/api';

export default function IncidentAssignment({ incidentId, currentAssignee, token, onUpdate }) {
  const [assignee, setAssignee] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAssign = async (e) => {
    e.preventDefault();
    if (!assignee.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/incidents/${incidentId}/assign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ assignee: assignee.trim() })
      });
      if (res.ok) {
        setAssignee('');
        if (onUpdate) onUpdate();
      } else {
        const data = await res.json();
        setError(data.detail || "Assignment failed");
      }
    } catch (err) {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 border border-white/5 rounded-xl p-4">
      <h4 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
        <UserPlus className="w-4 h-4 text-gray-400" /> Assignment
      </h4>
      
      {currentAssignee ? (
        <div className="flex items-center gap-2 p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
          <UserCheck className="w-5 h-5 text-indigo-400" />
          <div>
            <p className="text-xs text-gray-400">Currently Assigned To</p>
            <p className="text-sm font-bold text-indigo-300">{currentAssignee}</p>
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-2 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg mb-4">
          <AlertTriangle className="w-5 h-5 text-yellow-400" />
          <p className="text-xs text-yellow-300 font-medium">Unassigned - Needs Attention</p>
        </div>
      )}

      <form onSubmit={handleAssign} className="mt-4 flex flex-col gap-2">
        <label className="text-[10px] text-gray-500 font-bold uppercase">Reassign / Assign</label>
        <div className="flex gap-2">
          <input
            type="text"
            value={assignee}
            onChange={e => setAssignee(e.target.value)}
            placeholder="Username..."
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!assignee.trim() || loading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg disabled:opacity-50 transition-colors"
          >
            Assign
          </button>
        </div>
        {error && <p className="text-xs text-red-400 mt-1">{error}</p>}
      </form>
    </div>
  );
}
