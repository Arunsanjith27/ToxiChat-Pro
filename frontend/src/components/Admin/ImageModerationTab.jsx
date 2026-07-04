import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, Image as ImageIcon, ShieldAlert, CheckCircle, AlertTriangle, FileText, Activity, AlertCircle, X } from 'lucide-react';
import { adminApi } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export default function ImageModerationTab() {
  const { user } = useAuth();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (selected) {
      if (!selected.type.startsWith('image/')) {
        setError('Please select an image file.');
        return;
      }
      setFile(selected);
      setPreview(URL.createObjectURL(selected));
      setResult(null);
      setError('');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      if (!droppedFile.type.startsWith('image/')) {
        setError('Please drop an image file.');
        return;
      }
      setFile(droppedFile);
      setPreview(URL.createObjectURL(droppedFile));
      setResult(null);
      setError('');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const clearSelection = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const response = await adminApi.analyzeImage(file, user.access_token);
      setResult(response);
    } catch (err) {
      setError(err.message || 'Failed to analyze image.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL': return 'text-red-500 bg-red-500/10 border-red-500/20';
      case 'HIGH': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
      case 'MEDIUM': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      case 'LOW': return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold theme-text flex items-center gap-2">
            <ImageIcon className="w-6 h-6 text-indigo-400" />
            Image Moderation Engine
          </h2>
          <p className="theme-muted text-sm mt-1">Upload an image to analyze for OCR, PII, NSFW content, and Risk.</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Upload Column */}
        <div className="space-y-4">
          <div 
            className={`border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all ${
              preview ? 'border-indigo-500/30 bg-indigo-500/5' : 'border-white/10 hover:border-white/20 bg-black/20'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            {preview ? (
              <div className="relative w-full max-w-sm mx-auto">
                <img src={preview} alt="Preview" className="rounded-xl shadow-lg object-contain w-full max-h-64" />
                <button 
                  onClick={clearSelection}
                  className="absolute -top-3 -right-3 p-1.5 bg-red-500 hover:bg-red-600 text-white rounded-full shadow-lg transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <>
                <div className="w-16 h-16 rounded-full bg-indigo-500/10 flex items-center justify-center mb-4">
                  <Upload className="w-8 h-8 text-indigo-400" />
                </div>
                <h3 className="theme-text font-medium mb-2">Drag and drop your image here</h3>
                <p className="theme-muted text-sm mb-4">PNG, JPG, JPEG up to 5MB</p>
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className="btn-secondary px-6 py-2 rounded-xl text-sm"
                >
                  Browse Files
                </button>
              </>
            )}
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              accept="image/*" 
              onChange={handleFileChange}
            />
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-200/90">{error}</p>
            </div>
          )}

          <div className="flex justify-end">
            <button
              onClick={handleAnalyze}
              disabled={!file || loading}
              className={`btn-primary px-8 py-3 rounded-xl flex items-center gap-2 ${(!file || loading) ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {loading ? (
                <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Analyzing...</>
              ) : (
                <><Activity className="w-4 h-4" /> Analyze Image</>
              )}
            </button>
          </div>
        </div>

        {/* Results Column */}
        <div className="glass-panel rounded-2xl p-6 h-full flex flex-col">
          <h3 className="text-lg font-semibold theme-text mb-4 border-b border-white/5 pb-2">Analysis Results</h3>
          
          {!result && !loading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 opacity-50">
              <ShieldAlert className="w-12 h-12 text-gray-400 mb-3" />
              <p className="theme-muted text-sm">Upload and analyze an image to see results here.</p>
            </div>
          )}

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center space-y-4">
              <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
              <p className="text-indigo-400 text-sm animate-pulse">Running AI Models...</p>
            </div>
          )}

          {result && !loading && (
            <div className="space-y-6 overflow-y-auto pr-2">
              {/* Risk Banner */}
              <div className={`p-4 rounded-xl border flex items-center gap-4 ${getRiskColor(result.risk?.overall_risk)}`}>
                <div className="flex-1">
                  <p className="text-xs font-bold tracking-wider mb-1 opacity-80">OVERALL RISK LEVEL</p>
                  <div className="flex items-end gap-2">
                    <h4 className="text-2xl font-black">{result.risk?.overall_risk || 'UNKNOWN'}</h4>
                    <span className="text-sm font-medium mb-1 opacity-80">(Score: {result.risk?.risk_score || 0})</span>
                  </div>
                </div>
                <div className="text-right flex-1">
                  <p className="text-xs font-bold tracking-wider mb-1 opacity-80">RECOMMENDATION</p>
                  <p className="font-semibold text-sm">{result.explanation?.recommendations?.join(', ') || 'No recommendation provided.'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* NSFW Score */}
                <div className="bg-black/20 rounded-xl p-4 border border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs theme-muted font-bold">NSFW SCORE</p>
                    {(result.vision?.nsfw_score || 0) > 0.5 ? <AlertTriangle className="w-4 h-4 text-orange-400" /> : <CheckCircle className="w-4 h-4 text-emerald-400" />}
                  </div>
                  <p className={`text-xl font-bold ${(result.vision?.nsfw_score || 0) > 0.5 ? 'text-orange-400' : 'text-emerald-400'}`}>
                    {((result.vision?.nsfw_score || 0) * 100).toFixed(1)}%
                  </p>
                </div>

                {/* PII Detection */}
                <div className="bg-black/20 rounded-xl p-4 border border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs theme-muted font-bold">PII DETECTED</p>
                    {result.text_analysis?.contains_pii ? <AlertTriangle className="w-4 h-4 text-amber-400" /> : <CheckCircle className="w-4 h-4 text-emerald-400" />}
                  </div>
                  <p className={`text-xl font-bold ${result.text_analysis?.contains_pii ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {result.text_analysis?.contains_pii ? 'Yes' : 'None'}
                  </p>
                </div>
              </div>

              {/* OCR Text */}
              <div className="space-y-2">
                <h4 className="text-sm font-semibold theme-text flex items-center gap-2">
                  <FileText className="w-4 h-4 text-indigo-400" />
                  Extracted Text (OCR)
                </h4>
                <div className="bg-black/30 p-3 rounded-lg border border-white/5 text-sm theme-muted min-h-[80px] max-h-40 overflow-y-auto font-mono whitespace-pre-wrap">
                  {result.ocr?.text || <span className="italic opacity-50">No text detected in image.</span>}
                </div>
              </div>

              {/* PII Details if any */}
              {result.text_analysis?.contains_pii && result.text_analysis?.pii_entities?.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold theme-text">Detected PII</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.text_analysis.pii_entities.map((pii, idx) => (
                      <span key={idx} className="px-2 py-1 rounded bg-amber-500/20 text-amber-300 text-xs border border-amber-500/30">
                        {pii.entity_type || pii}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Emotion */}
              {result.text_analysis?.emotion && (
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold theme-text">Detected Emotion</h4>
                  <span className="px-3 py-1 rounded bg-violet-500/20 text-violet-300 text-xs border border-violet-500/30 capitalize">
                    {result.text_analysis.emotion}
                  </span>
                </div>
              )}

              {/* Explanation Reasoning */}
              {result.explanation?.primary_reasons?.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold theme-text">Risk Reasoning</h4>
                  <div className="space-y-1">
                    {result.explanation.primary_reasons.map((reason, idx) => (
                      <div key={idx} className="p-2 rounded-lg bg-black/20 border border-white/5 text-sm theme-muted">
                        <span className={`text-xs font-bold mr-2 ${reason.severity === 'LOW' ? 'text-emerald-400' : reason.severity === 'MEDIUM' ? 'text-amber-400' : 'text-red-400'}`}>
                          {reason.severity}
                        </span>
                        {reason.message}
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
