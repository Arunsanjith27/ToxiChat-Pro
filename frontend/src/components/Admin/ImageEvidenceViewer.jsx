import React, { useState } from 'react';
import { Upload, ImageIcon, ShieldAlert, FileText, Download, Activity, ScanFace, FileSearch } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { adminApi } from '../../services/api';

export default function ImageEvidenceViewer() {
  const { user } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setError("File exceeds 5MB limit.");
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
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
      const data = await adminApi.analyzeImage(selectedFile, user.access_token);
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const exportPDF = () => {
    if (!analysis) return;
    
    // Simulate PDF generation for the Evidence Package
    const content = `TOXICHAT PRO - EVIDENCE PACKAGE\n\n` +
      `Date: ${new Date().toISOString()}\n` +
      `Image Hash (SHA-256): ${analysis.image.hash}\n` +
      `Size: ${analysis.image.size_bytes} bytes\n\n` +
      `[VISION ANALYSIS]\n` +
      `NSFW Score: ${analysis.vision.nsfw_score.toFixed(4)}\n` +
      `Violence Score: ${analysis.vision.violence_score.toFixed(4)}\n\n` +
      `[OCR TEXT]\n` +
      `Confidence: ${analysis.ocr.confidence?.toFixed(4)}\n` +
      `${analysis.ocr.text || 'No text extracted'}\n\n` +
      `[TEXT SAFETY]\n` +
      `Toxicity: ${analysis.text_analysis?.toxicity || 0}\n` +
      `Emotion: ${analysis.text_analysis?.emotion || 'Neutral'}\n` +
      `PII Present: ${analysis.text_analysis?.contains_pii ? 'YES' : 'NO'}\n` +
      (analysis.text_analysis?.pii_entities?.length > 0 ? `PII Entities: ${analysis.text_analysis.pii_entities.map(e => e.entity_type || e).join(', ')}\n\n` : '\n') +
      `[OVERALL RISK]\n` +
      `Level: ${analysis.risk.overall_risk}\n` +
      `Score: ${analysis.risk.risk_score}\n` +
      `Recommendation: ${analysis.risk.recommendation || 'N/A'}\n` +
      `Alerts: ${JSON.stringify(analysis.explanation)}`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `evidence-${analysis.image.hash.substring(0,8)}.txt`; // txt for now as mockup
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-gray-900 border border-white/10 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <ScanFace className="w-6 h-6 text-indigo-400" />
          Image Evidence Inspector
        </h2>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Left Side: Upload & Preview */}
        <div className="space-y-4">
          <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center bg-black/20 hover:bg-black/40 transition-colors">
            <input 
              type="file" 
              accept="image/jpeg, image/png, image/webp" 
              className="hidden" 
              id="img-upload" 
              onChange={handleFileChange} 
            />
            <label htmlFor="img-upload" className="cursor-pointer flex flex-col items-center gap-3">
              <Upload className="w-8 h-8 text-indigo-400" />
              <div className="text-sm font-medium text-gray-300">
                Click to browse or drag and drop image
              </div>
              <p className="text-xs text-gray-500">JPG, PNG, WEBP up to 5MB</p>
            </label>
          </div>

          {error && <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-lg">{error}</div>}

          {previewUrl && (
            <div className="relative rounded-xl overflow-hidden border border-white/10 bg-black/50 aspect-video flex items-center justify-center">
              <img src={previewUrl} alt="Preview" className="max-h-full max-w-full object-contain" />
              
              {/* Optional: Draw OCR bounding boxes over the image if we had dimensions synced */}
            </div>
          )}

          <button 
            onClick={uploadAndAnalyze}
            disabled={!selectedFile || loading}
            className="w-full btn-primary p-3 rounded-xl flex items-center justify-center gap-2"
          >
            {loading ? <Activity className="w-5 h-5 animate-spin" /> : <FileSearch className="w-5 h-5" />}
            {loading ? 'Running AI Models...' : 'Analyze Image'}
          </button>
        </div>

        {/* Right Side: Results */}
        <div className="bg-black/30 rounded-xl border border-white/5 p-5 min-h-[400px]">
          {!analysis ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-3">
              <ImageIcon className="w-12 h-12 opacity-50" />
              <p className="text-sm">Upload an image to see deep AI analysis</p>
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
                    Score: {analysis.risk.risk_score}
                  </span>
                </div>
                <button onClick={exportPDF} className="p-2 bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 rounded-lg flex items-center gap-1 text-xs font-medium transition-colors">
                  <Download className="w-4 h-4" /> Export Evidence
                </button>
              </div>

              {/* SHA-256 Hash and Image Meta */}
              <div className="p-3 bg-gray-900 rounded-lg border border-gray-800">
                <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Image Metadata</p>
                <p className="text-xs text-gray-300 font-mono break-all">Hash: {analysis.image.hash}</p>
                <p className="text-xs text-gray-400 font-mono mt-1">MIME: {analysis.image.mime_type} | Size: {(analysis.image.size_bytes / 1024).toFixed(2)} KB</p>
              </div>

              {/* Vision vs Text Grid */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-gray-800/50 rounded-lg border border-white/5">
                  <p className="text-xs text-gray-400 flex items-center gap-1 mb-2"><ScanFace className="w-3 h-3" /> Vision AI</p>
                  <p className="text-sm font-medium text-white flex justify-between">NSFW: <span className={analysis.vision.nsfw_score > 0.6 ? 'text-red-400' : 'text-gray-300'}>{(analysis.vision.nsfw_score * 100).toFixed(1)}%</span></p>
                  <p className="text-sm font-medium text-white flex justify-between mt-1">Violence: <span className={analysis.vision.violence_score > 0.6 ? 'text-red-400' : 'text-gray-300'}>{(analysis.vision.violence_score * 100).toFixed(1)}%</span></p>
                </div>
                
                <div className="p-3 bg-gray-800/50 rounded-lg border border-white/5">
                  <p className="text-xs text-gray-400 flex items-center gap-1 mb-2"><FileText className="w-3 h-3" /> Text AI (OCR)</p>
                  <p className="text-sm font-medium text-white flex justify-between">Toxicity: <span className={analysis.text_analysis?.toxicity > 0.5 ? 'text-red-400' : 'text-gray-300'}>{analysis.text_analysis?.toxicity != null ? (analysis.text_analysis.toxicity * 100).toFixed(0) + '%' : '0%'}</span></p>
                  <p className="text-sm font-medium text-white flex justify-between mt-1">Emotion: <span className="text-gray-300">{analysis.text_analysis?.emotion || 'Neutral'}</span></p>
                  <p className="text-sm font-medium text-white flex justify-between mt-1">PII: <span className={analysis.text_analysis?.contains_pii ? 'text-red-400' : 'text-gray-300'}>{analysis.text_analysis?.contains_pii ? 'YES' : 'NO'}</span></p>
                </div>
              </div>
              
              {/* PII Details if any */}
              {analysis.text_analysis?.contains_pii && analysis.text_analysis?.pii_entities?.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold theme-text text-white">Detected PII</h4>
                  <div className="flex flex-wrap gap-2">
                    {analysis.text_analysis.pii_entities.map((pii, idx) => (
                      <span key={idx} className="px-2 py-1 rounded bg-amber-500/20 text-amber-300 text-xs border border-amber-500/30">
                        {pii.entity_type || pii}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* OCR Text Box */}
              <div>
                <p className="text-xs font-medium text-gray-400 mb-2 flex items-center gap-1"><FileText className="w-4 h-4"/> Extracted Text (Conf: {analysis.ocr.confidence ? (analysis.ocr.confidence * 100).toFixed(1) + '%' : 'N/A'})</p>
                <div className="bg-black p-3 rounded-lg border border-gray-800 max-h-32 overflow-y-auto text-sm text-gray-300 font-mono">
                  {analysis.ocr.text || <span className="text-gray-600 italic">No text detected in image.</span>}
                </div>
              </div>

              {/* Explainability */}
              {Object.keys(analysis.explanation || {}).length > 0 && (
                <div>
                   <p className="text-xs font-medium text-red-400 mb-2 flex items-center gap-1"><ShieldAlert className="w-4 h-4"/> Alerts</p>
                   <ul className="text-xs text-gray-300 space-y-1 list-disc pl-4">
                     {Object.entries(analysis.explanation).map(([key, val]) => (
                       <li key={key}>{val}</li>
                     ))}
                   </ul>
                </div>
              )}
              
              {analysis.risk.recommendation && (
                <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
                  <p className="text-xs font-bold text-indigo-400 mb-1">Recommendation</p>
                  <p className="text-sm text-indigo-200">{analysis.risk.recommendation}</p>
                </div>
              )}
              
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
