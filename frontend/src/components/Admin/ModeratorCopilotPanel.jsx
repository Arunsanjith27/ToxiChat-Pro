import React, { useState } from 'react';
import { Send, Cpu, Sparkles, ShieldCheck, Download, Server, AlertCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { API_URL } from '../../services/api';

export default function ModeratorCopilotPanel({ conversationId, participants, isGroup }) {
  const { user } = useAuth();
  const [query, setQuery] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const quickPrompts = [
    "Why was this conversation flagged?",
    "Summarize this incident.",
    "Explain the current prediction.",
    "Recommend moderator actions.",
    "Show all PII exposure.",
    "Summarize image evidence."
  ];

  const handleAsk = async (text) => {
    if (!text || !text.trim() || !conversationId) return;

    const currentQuery = text;
    setQuery('');
    setLoading(true);

    // Add user query to history immediately
    const userMsg = { role: 'user', text: currentQuery };
    setHistory(prev => [...prev, userMsg]);

    try {
      const res = await fetch(`${API_URL}/api/admin/copilot`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.access_token}`
        },
        body: JSON.stringify({ 
          conversation_id: conversationId, 
          question: currentQuery,
          participants: participants,
          is_group: isGroup
        })
      });

      if (!res.ok) throw new Error("Copilot Engine failed to respond.");

      const data = await res.json();
      
      const copilotMsg = { 
        role: 'ai', 
        text: data.answer,
        confidence: data.confidence,
        sources: data.sources,
        recommendations: data.recommendations
      };

      setHistory(prev => [...prev, copilotMsg]);

    } catch (err) {
      console.error(err);
      setHistory(prev => [...prev, { role: 'ai', text: "Error connecting to AI Copilot Engine." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (history.length === 0) return;
    
    let content = `TOXICHAT PRO - COPILOT INVESTIGATION REPORT\n`;
    content += `Conversation ID: ${conversationId}\n`;
    content += `Date: ${new Date().toISOString()}\n\n`;
    
    history.forEach(h => {
      if (h.role === 'user') {
        content += `[MODERATOR QUERY]\n${h.text}\n\n`;
      } else {
        content += `[AI COPILOT RESPONSE]\n${h.text}\n`;
        if (h.sources?.length > 0) content += `Sources: ${h.sources.join(', ')}\n`;
        if (h.confidence) content += `Confidence: ${(h.confidence * 100).toFixed(0)}%\n`;
        if (h.recommendations?.length > 0) {
          content += `Recommended Actions: ${h.recommendations.map(r => r.action).join(', ')}\n`;
        }
        content += `\n`;
      }
    });

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `copilot-report-${conversationId.substring(0,8)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-gray-900 border border-white/10 rounded-2xl overflow-hidden shadow-xl flex flex-col h-[600px]">
      
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900/40 to-indigo-900/40 p-4 border-b border-white/5 flex justify-between items-center shrink-0">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-blue-400" />
          AI Moderator Copilot
        </h3>
        <button 
          onClick={handleExport}
          className="p-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 rounded-lg flex items-center gap-1 text-xs font-medium transition-colors"
        >
          <Download className="w-4 h-4" /> Export Report
        </button>
      </div>

      {/* Quick Prompts & Chat History */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        
        {history.length === 0 && (
          <div className="text-center py-10">
            <Sparkles className="w-12 h-12 text-blue-500/50 mx-auto mb-4" />
            <p className="text-gray-400 text-sm mb-6">Ask a question to investigate this conversation using AI.</p>
            
            <div className="flex flex-wrap justify-center gap-2 px-4">
              {quickPrompts.map((prompt, i) => (
                <button 
                  key={i} 
                  onClick={() => handleAsk(prompt)}
                  className="px-3 py-2 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 rounded-lg text-blue-300 text-xs transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {history.map((msg, idx) => (
          <div key={idx} className={`flex flex-col max-w-[85%] ${msg.role === 'user' ? 'self-end ml-auto' : 'self-start mr-auto'}`}>
            <div className={`p-4 rounded-2xl ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-none' : 'bg-gray-800 text-gray-200 border border-white/5 rounded-tl-none'}`}>
              <p className="text-sm">{msg.text}</p>
              
              {msg.role === 'ai' && (
                <div className="mt-3 pt-3 border-t border-white/5 space-y-2">
                  
                  {/* Confidence & Sources */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="flex items-center gap-1 text-[10px] text-gray-400 bg-black/40 px-2 py-1 rounded">
                        <ShieldCheck className="w-3 h-3 text-emerald-400" />
                        Confidence: {(msg.confidence * 100).toFixed(0)}%
                      </span>
                      <span className="flex items-center gap-1 text-[10px] text-gray-400 bg-black/40 px-2 py-1 rounded">
                        <Server className="w-3 h-3 text-blue-400" />
                        Sources: {msg.sources.join(', ')}
                      </span>
                    </div>
                  )}

                  {/* Recommended Actions */}
                  {msg.recommendations && msg.recommendations.length > 0 && (
                    <div className="mt-2">
                      <p className="text-[10px] text-gray-400 font-bold uppercase mb-1">Recommended Actions</p>
                      <div className="flex flex-wrap gap-1">
                        {msg.recommendations.map((r, i) => (
                          <span key={i} className={`text-[10px] font-medium px-2 py-1 rounded border ${r.priority === 'CRITICAL' || r.priority === 'HIGH' ? 'bg-red-500/20 border-red-500/30 text-red-300' : 'bg-indigo-500/20 border-indigo-500/30 text-indigo-300'}`}>
                            {r.action}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                </div>
              )}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="self-start mr-auto p-4 rounded-2xl rounded-tl-none bg-gray-800 border border-white/5">
             <div className="flex gap-1 items-center h-4">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
             </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 bg-black/40 border-t border-white/5 shrink-0">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleAsk(query); }}
          className="flex items-center gap-2 bg-gray-800 border border-gray-700 rounded-xl p-1"
        >
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask the AI Copilot to investigate..."
            className="flex-1 bg-transparent border-none text-sm text-white px-4 py-2 focus:outline-none"
            disabled={loading}
          />
          <button 
            type="submit" 
            disabled={!query.trim() || loading}
            className="p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

    </div>
  );
}
