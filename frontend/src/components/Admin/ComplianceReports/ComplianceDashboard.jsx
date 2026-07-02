import React, { useState } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { FileText, Download, FileJson, FileType, CheckCircle, RefreshCw } from 'lucide-react';

export default function ComplianceDashboard() {
  const { user } = useAuth();
  const [incidentId, setIncidentId] = useState('');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateReport = async (e) => {
    e.preventDefault();
    if (!incidentId.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const res = await fetch('/api/reports/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.access_token}`
        },
        body: JSON.stringify({ incident_id: incidentId.trim() })
      });
      
      if (res.ok) {
        const data = await res.json();
        setReport(data);
      } else {
        const data = await res.json();
        setError(data.detail || "Failed to generate report");
      }
    } catch (err) {
      setError("Network error generating report.");
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = (format) => {
    if (!report) return;
    window.open(`/api/reports/download/${report.report_id}?format=${format}`, '_blank');
  };

  return (
    <div className="flex flex-col h-full bg-black">
      {/* Header */}
      <div className="p-6 bg-gray-900 border-b border-white/5 shrink-0">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <FileText className="w-6 h-6 text-emerald-500" /> Enterprise Compliance Reports
        </h1>
        <p className="text-sm text-gray-400 mt-1">Generate immutable, cryptographically verifiable case reports.</p>
      </div>

      <div className="p-6 flex-1 overflow-y-auto">
        {!report ? (
          <div className="max-w-xl mx-auto mt-10">
            <div className="bg-gray-900 border border-white/10 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Generate Report</h2>
              <form onSubmit={generateReport} className="flex flex-col gap-4">
                <div>
                  <label className="text-xs text-gray-400 font-bold uppercase mb-1 block">Incident ID</label>
                  <input
                    type="text"
                    value={incidentId}
                    onChange={(e) => setIncidentId(e.target.value)}
                    placeholder="Enter an Incident ID to compile..."
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500"
                    disabled={loading}
                  />
                </div>
                <button
                  type="submit"
                  disabled={!incidentId.trim() || loading}
                  className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {loading ? <RefreshCw className="w-5 h-5 animate-spin" /> : "Compile Enterprise Report"}
                </button>
                {error && <p className="text-sm text-red-400 text-center">{error}</p>}
              </form>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
              <button 
                onClick={() => setReport(null)}
                className="text-sm text-gray-400 hover:text-white transition-colors"
              >
                &larr; Back to Generator
              </button>
              
              <div className="flex gap-2">
                <button onClick={() => downloadReport('pdf')} className="px-3 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 rounded-lg text-sm flex items-center gap-2 transition-colors">
                  <Download className="w-4 h-4" /> PDF
                </button>
                <button onClick={() => downloadReport('md')} className="px-3 py-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 rounded-lg text-sm flex items-center gap-2 transition-colors">
                  <FileType className="w-4 h-4" /> Markdown
                </button>
                <button onClick={() => downloadReport('json')} className="px-3 py-2 bg-yellow-500/10 hover:bg-yellow-500/20 text-yellow-400 border border-yellow-500/20 rounded-lg text-sm flex items-center gap-2 transition-colors">
                  <FileJson className="w-4 h-4" /> JSON
                </button>
              </div>
            </div>

            <div className="bg-gray-900 border border-emerald-500/30 rounded-xl p-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-bl-full -z-0"></div>
              
              <div className="flex justify-between items-start mb-8 relative z-10 border-b border-white/10 pb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">Compliance Report</h2>
                  <p className="text-sm text-gray-400 font-mono">ID: {report.report_id.split('-')[0]}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500 font-bold uppercase mb-1">Status</p>
                  <p className="text-emerald-400 font-bold flex items-center gap-1 justify-end">
                    <CheckCircle className="w-4 h-4" /> FINAL
                  </p>
                </div>
              </div>

              <div className="space-y-6 relative z-10 text-gray-300 text-sm">
                <section>
                  <h3 className="text-white font-bold mb-3 border-b border-white/5 pb-2">Digital Signature</h3>
                  <div className="bg-black/50 p-4 rounded-lg font-mono text-xs break-all border border-white/5 text-gray-500">
                    <span className="text-emerald-500 font-bold">SHA-256:</span> {report.report_hash}
                  </div>
                </section>

                <section className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-white font-bold mb-3 border-b border-white/5 pb-2">Metadata</h3>
                    <ul className="space-y-2">
                      <li><span className="text-gray-500">Generated:</span> {new Date(report.generated_at).toLocaleString()}</li>
                      <li><span className="text-gray-500">Author:</span> {report.generated_by}</li>
                      <li><span className="text-gray-500">System Ver:</span> {report.system_version}</li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="text-white font-bold mb-3 border-b border-white/5 pb-2">Incident Overview</h3>
                    <ul className="space-y-2">
                      <li><span className="text-gray-500">Priority:</span> {report.report_object.incident_overview.priority}</li>
                      <li><span className="text-gray-500">Status:</span> {report.report_object.incident_overview.status}</li>
                      <li><span className="text-gray-500">Assignee:</span> {report.report_object.incident_overview.assigned_moderator || 'None'}</li>
                    </ul>
                  </div>
                </section>

                <section>
                  <h3 className="text-white font-bold mb-3 border-b border-white/5 pb-2">AI Executive Summary</h3>
                  <p className="bg-indigo-900/20 p-4 rounded-lg border border-indigo-500/20 leading-relaxed text-indigo-100">
                    {report.report_object.copilot_snapshot.answer || "No AI summary available."}
                  </p>
                </section>
                
                <section>
                  <h3 className="text-white font-bold mb-3 border-b border-white/5 pb-2">Audit Ledger ({report.report_object.timeline.length} events)</h3>
                  <div className="bg-black/50 rounded-lg p-4 border border-white/5 max-h-60 overflow-y-auto font-mono text-xs space-y-2">
                    {report.report_object.timeline.map(log => (
                       <div key={log.audit_id} className="flex gap-4">
                         <span className="text-gray-500 w-32 shrink-0">{new Date(log.timestamp).toLocaleTimeString()}</span>
                         <span className="text-blue-400 w-24 shrink-0">{log.actor_username}</span>
                         <span className="text-emerald-400 w-40 shrink-0">{log.action}</span>
                         <span className="text-gray-400 truncate">{log.description}</span>
                       </div>
                    ))}
                  </div>
                </section>
                
                <div className="mt-8 pt-8 border-t border-white/10 text-center text-xs text-gray-600">
                  <p>CONFIDENTIAL ENTERPRISE DOCUMENT - TOXICHAT PRO COMPLIANCE ENGINE</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
