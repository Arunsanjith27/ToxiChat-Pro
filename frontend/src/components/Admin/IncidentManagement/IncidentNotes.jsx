import React, { useState, useEffect } from 'react';
import { Send, Lock, User } from 'lucide-react';

export default function IncidentNotes({ incidentId, token }) {
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchNotes = async () => {
    try {
      const res = await fetch(`/api/incidents/${incidentId}/notes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setNotes(data);
      }
    } catch (err) {
      console.error("Failed to fetch notes", err);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, [incidentId]);

  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNote.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/incidents/${incidentId}/notes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content: newNote, internal_only: true })
      });
      if (res.ok) {
        setNewNote('');
        fetchNotes();
      }
    } catch (err) {
      console.error("Failed to add note", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 border border-white/5 rounded-xl overflow-hidden">
      <div className="p-3 bg-black/40 border-b border-white/5 flex items-center gap-2">
        <Lock className="w-4 h-4 text-gray-400" />
        <h4 className="text-sm font-semibold text-gray-200">Internal Notes</h4>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[200px] max-h-[400px]">
        {notes.length === 0 && (
          <p className="text-xs text-gray-500 text-center italic mt-10">No investigation notes yet.</p>
        )}
        {notes.map(note => (
          <div key={note.note_id} className="bg-gray-800 rounded-lg p-3 border border-white/5">
            <div className="flex justify-between items-start mb-2">
              <span className="flex items-center gap-1 text-xs font-medium text-indigo-400">
                <User className="w-3 h-3" /> {note.author}
              </span>
              <span className="text-[10px] text-gray-500">
                {new Date(note.timestamp).toLocaleString()}
              </span>
            </div>
            <p className="text-sm text-gray-300 whitespace-pre-wrap">{note.content}</p>
          </div>
        ))}
      </div>

      <div className="p-3 bg-black/40 border-t border-white/5">
        <form onSubmit={handleAddNote} className="flex gap-2">
          <input
            type="text"
            value={newNote}
            onChange={e => setNewNote(e.target.value)}
            placeholder="Add an internal note..."
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!newNote.trim() || loading}
            className="p-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg disabled:opacity-50 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
