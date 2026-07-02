import React, { useState, useRef } from 'react';
import { Upload, Mic, ShieldAlert, FileText, Download, Activity, FileAudio, PlayCircle, Clock } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function AudioEvidenceViewer() {
  const { user } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const audioRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 20 * 1024 * 1024) {
        setError("File exceeds 20MB limit.");
        return;
      }
      setSelectedFile(file);
      setAudioUrl(URL.createObjectURL(file));
      setAnalysis(null);
      setError('');
    }
  };

  const uploadAndAnalyze = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError('');
    setAnalysis(null);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch('/api/audio/analyze', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.access_token}`
        },
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Upload failed');
      }

      const data = await res.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const jumpToTime = (seconds) => {
    if (audioRef.current) {
      audioRef.current.currentTime = seconds;
      audioRef.current.play();
    }
  };

  const exportPDF = () => {
    if (!analysis) return;
    
    // Simulate PDF Evidence Package Export
    const content = `TOXICHAT PRO - AUDIO EVIDENCE PACKAGE\n\n` +
      `Date: ${new Date().toISOString()}\n` +
      `Audio Hash (SHA-256): ${analysis.audio.hash}\n` +
      `Duration: ${analysis.audio.duration.toFixed(2)}s | Language: ${analysis.audio.language}\n\n` +
      `[TRANSCRIPT]\n` +
      `${analysis.transcript.text || 'No speech detected'}\n\n` +
      `[TEXT SAFETY]\n` +
      `Toxicity: ${analysis.text_analysis?.toxicity || 0}\n` +
      `Emotion: ${analysis.text_analysis?.emotion || 'Neutral'}\n` +
      `PII Present: ${analysis.text_analysis?.contains_pii ? 'YES' : 'NO'}\n\n` +
      `[OVERALL RISK]\n` +
      `Level: ${analysis.risk.overall_risk}\n` +
      `Score: ${analysis.risk.risk_score}\n` +
      `Alerts: ${JSON.stringify(analysis.explanation)}`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audio-evidence-${analysis.audio.hash.substring(0,8)}.txt`; 
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-gray-900 border border-white/10 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Mic className="w-6 h-6 text-purple-400" />
          Audio Evidence Inspector
        </h2>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Left Side: Upload & Audio Player */}
        <div className="space-y-4">
          <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center bg-black/20 hover:bg-black/40 transition-colors">
            <input 
              type="file" 
              accept="audio/wav, audio/mpeg, audio/mp3, audio/ogg, audio/mp4" 
              className="hidden" 
              id="audio-upload" 
              onChange={handleFileChange} 
            />
            <label htmlFor="audio-upload" className="cursor-pointer flex flex-col items-center gap-3">
              <Upload className="w-8 h-8 text-purple-400" />
              <div className="text-sm font-medium text-gray-300">
                Click to browse or drag and drop audio
              </div>
              <p className="text-xs text-gray-500">MP3, WAV, OGG, MP4 up to 20MB</p>
            </label>
          </div>

          {error && <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-lg">{error}</div>}

          {audioUrl && (
            <div className="p-4 bg-black/30 border border-white/10 rounded-xl">
              <audio ref={audioRef} controls src={audioUrl} className="w-full mb-2 outline-none" />
              <div className="text-[10px] text-gray-500 flex justify-between px-2">
                <span>{selectedFile.name}</span>
                <span>{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</span>
              </div>
            </div>
          )}

          <button 
            onClick={uploadAndAnalyze}
            disabled={!selectedFile || loading}
            className="w-full btn-primary !bg-purple-600 hover:!bg-purple-700 p-3 rounded-xl flex items-center justify-center gap-2 transition-colors"
          >
            {loading ? <Activity className="w-5 h-5 animate-spin" /> : <FileAudio className="w-5 h-5" />}
            {loading ? 'Running Whisper AI...' : 'Transcribe & Analyze Audio'}
          </button>
        </div>

        {/* Right Side: Results */}
        <div className="bg-black/30 rounded-xl border border-white/5 p-5 min-h-[400px]">
          {!analysis ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-3">
              <Mic className="w-12 h-12 opacity-50" />
              <p className="text-sm text-center">Upload audio to generate forensic<br/>transcripts and AI safety metadata</p>
            </div>
          ) : (
            <div className="space-y-5">
              {/* Top Meta */}
              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  <span className={`px-2 py-1 text-xs font-bold rounded-md ${analysis.risk.overall_risk === 'CRITICAL' || analysis.risk.overall_risk === 'HIGH' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                    {analysis.risk.overall_risk} RISK
                  </span>
                  <span className="px-2 py-1 text-xs font-medium bg-gray-800 text-gray-300 rounded-md">
                    Language: {analysis.audio.language.toUpperCase()}
                  </span>
                </div>
                <button onClick={exportPDF} className="p-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 rounded-lg flex items-center gap-1 text-xs font-medium transition-colors">
                  <Download className="w-4 h-4" /> Export Evidence
                </button>
              </div>

              {/* SHA-256 Hash */}
              <div className="p-3 bg-gray-900 rounded-lg border border-gray-800 flex justify-between items-center">
                 <div>
                   <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">SHA-256 Fingerprint</p>
                   <p className="text-xs text-gray-300 font-mono break-all">{analysis.audio.hash.substring(0,24)}...</p>
                 </div>
                 <div className="text-right">
                   <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Confidence</p>
                   <p className="text-xs text-purple-400 font-bold">{(analysis.transcript.confidence * 100).toFixed(1)}%</p>
                 </div>
              </div>

              {/* Text AI */}
              <div className="p-3 bg-gray-800/50 rounded-lg border border-white/5">
                <p className="text-xs text-gray-400 flex items-center gap-1 mb-2"><FileText className="w-3 h-3" /> Content AI Analytics</p>
                <div className="flex justify-between items-center text-sm font-medium">
                  <span className="text-white">Toxicity: <span className={analysis.text_analysis?.toxicity > 0.5 ? 'text-red-400' : 'text-gray-300'}>{analysis.text_analysis?.toxicity ? (analysis.text_analysis.toxicity * 100).toFixed(0) + '%' : 'N/A'}</span></span>
                  <span className="text-white">Emotion: <span className="text-gray-300">{analysis.text_analysis?.emotion || 'Neutral'}</span></span>
                </div>
              </div>

              {/* Transcript Timeline */}
              <div>
                <p className="text-xs font-medium text-gray-400 mb-2 flex items-center gap-1"><Clock className="w-4 h-4"/> Transcription Timeline</p>
                <div className="bg-black p-3 rounded-lg border border-gray-800 max-h-48 overflow-y-auto space-y-3">
                  {analysis.transcript.segments && analysis.transcript.segments.length > 0 ? (
                    analysis.transcript.segments.map((seg, i) => (
                      <div key={i} className="flex gap-3 text-sm group">
                        <button 
                          onClick={() => jumpToTime(seg.start)}
                          className="text-purple-400 text-xs font-mono shrink-0 hover:text-purple-300 hover:underline pt-0.5"
                        >
                          [{new Date(seg.start * 1000).toISOString().substring(14, 19)}]
                        </button>
                        <p className="text-gray-300 leading-snug">{seg.text}</p>
                      </div>
                    ))
                  ) : (
                    <span className="text-gray-600 italic">No speech detected in audio.</span>
                  )}
                </div>
              </div>

              {/* Explainability */}
              {Object.keys(analysis.explanation || {}).length > 0 && (
                <div>
                   <p className="text-xs font-medium text-red-400 mb-2 flex items-center gap-1"><ShieldAlert className="w-4 h-4"/> Safety Alerts</p>
                   <ul className="text-xs text-gray-300 space-y-1 list-disc pl-4">
                     {Object.entries(analysis.explanation).map(([key, val]) => (
                       <li key={key}>{val}</li>
                     ))}
                   </ul>
                </div>
              )}
              
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
