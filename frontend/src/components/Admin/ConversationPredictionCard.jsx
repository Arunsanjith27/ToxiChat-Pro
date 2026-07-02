import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, TrendingUp, TrendingDown, Clock, ShieldAlert, Zap, Info } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function ConversationPredictionCard({ conversationId }) {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!conversationId) return;

    const fetchPrediction = async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/conversation/prediction/${conversationId}`, {
          headers: { 'Authorization': `Bearer ${user.access_token}` }
        });
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
      } catch (err) {
        console.error("Failed to load escalation prediction", err);
      } finally {
        setLoading(false);
      }
    };

    fetchPrediction();
    
    // Poll every 30 seconds for live investigations
    const interval = setInterval(fetchPrediction, 30000);
    return () => clearInterval(interval);
  }, [conversationId, user.access_token]);

  if (loading && !data) {
    return (
      <div className="glass-panel rounded-2xl p-6 flex flex-col items-center justify-center min-h-[300px]">
        <Activity className="w-8 h-8 text-indigo-400 animate-spin mb-4" />
        <p className="text-gray-400 font-medium">Predicting Escalation Trajectory...</p>
      </div>
    );
  }

  if (!data) return null;

  const { prediction, reasons, recommendations, timeline, metadata } = data;
  
  // Calculate Gauge colors
  const probPercent = prediction.probability * 100;
  let gaugeColor = "text-emerald-400";
  let gaugeBg = "stroke-emerald-500/20";
  if (probPercent > 75) {
    gaugeColor = "text-red-400";
    gaugeBg = "stroke-red-500/20";
  } else if (probPercent > 40) {
    gaugeColor = "text-yellow-400";
    gaugeBg = "stroke-yellow-500/20";
  }

  return (
    <div className="glass-panel rounded-2xl overflow-hidden relative">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-900 to-black p-4 border-b border-white/5 flex justify-between items-center">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Zap className="w-5 h-5 text-indigo-400" />
          Escalation Prediction Engine
        </h3>
        <div className="flex gap-2">
           <span className="px-2 py-1 bg-gray-800 text-gray-400 text-xs rounded-md border border-white/5">
             v{metadata.prediction_version}
           </span>
        </div>
      </div>

      <div className="p-6 grid lg:grid-cols-3 gap-8">
        
        {/* Left Column: Gauges */}
        <div className="space-y-6 flex flex-col items-center justify-center border-r border-white/5 pr-6">
          
          {/* Main Probability Gauge */}
          <div className="relative w-40 h-40 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" fill="transparent" strokeWidth="8" className={gaugeBg} />
              <circle 
                cx="50" cy="50" r="40" fill="transparent" strokeWidth="8" 
                stroke="currentColor" 
                className={`${gaugeColor} transition-all duration-1000 ease-out`}
                strokeDasharray={`${probPercent * 2.51} 251`}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className={`text-3xl font-black ${gaugeColor}`}>
                {probPercent.toFixed(0)}%
              </span>
              <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-1">
                Escalation<br/>Probability
              </span>
            </div>
          </div>
          
          {/* Metrics */}
          <div className="w-full space-y-3">
             <div className="flex justify-between items-center p-3 bg-black/40 rounded-lg border border-white/5">
               <span className="text-xs text-gray-400 font-medium">Predicted State</span>
               <span className={`text-xs font-bold px-2 py-1 rounded ${prediction.predicted_state === 'CRITICAL' || prediction.predicted_state === 'HIGH' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                 {prediction.predicted_state}
               </span>
             </div>
             
             <div className="flex justify-between items-center p-3 bg-black/40 rounded-lg border border-white/5">
               <span className="text-xs text-gray-400 font-medium">Confidence</span>
               <span className="text-xs text-white font-mono">
                 {(prediction.confidence * 100).toFixed(0)}%
               </span>
             </div>
             
             <div className="flex justify-between items-center p-3 bg-black/40 rounded-lg border border-white/5">
               <span className="text-xs text-gray-400 font-medium">Trend</span>
               <span className="text-xs text-white flex items-center gap-1">
                 {prediction.trend === 'ESCALATING' || prediction.trend === 'CRITICAL' ? <TrendingUp className="w-3 h-3 text-red-400"/> : <TrendingDown className="w-3 h-3 text-emerald-400"/>}
                 {prediction.trend}
               </span>
             </div>
          </div>
        </div>

        {/* Right Column: Context & Actions */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Expected Window */}
          <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-xl flex items-start gap-4">
            <div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400 mt-1">
               <Clock className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-indigo-300 mb-1">Expected Escalation Window</h4>
              <p className="text-xs text-gray-300 leading-relaxed">
                Based on current velocity and emotional density, this conversation is projected to hit {prediction.predicted_state} risk within <strong className="text-white">{prediction.expected_window}</strong> if no intervention occurs.
              </p>
            </div>
          </div>

          {/* Reasoning */}
          <div>
            <h4 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
              <Info className="w-4 h-4 text-gray-400" />
              Determinant Factors
            </h4>
            <div className="grid grid-cols-1 gap-2">
              {reasons.map((r, i) => (
                <div key={i} className="flex items-start gap-2 p-2.5 bg-gray-800/40 rounded-lg border border-gray-700/50">
                   <div className="w-1.5 h-1.5 rounded-full bg-gray-500 mt-1.5 shrink-0" />
                   <p className="text-xs text-gray-300">{r}</p>
                </div>
              ))}
              {reasons.length === 0 && <p className="text-xs text-gray-500 italic">No significant escalation factors detected.</p>}
            </div>
          </div>

          {/* Recommendations */}
          <div>
            <h4 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
              <ShieldAlert className="w-4 h-4 text-red-400" />
              Recommended Actions
            </h4>
            <div className="flex flex-wrap gap-2">
              {recommendations.map((rec, i) => (
                <button key={i} className={`text-xs font-medium px-4 py-2 rounded-lg border transition-colors ${
                  rec.priority === 'CRITICAL' || rec.priority === 'HIGH' 
                    ? 'bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20' 
                    : 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/20'
                }`}>
                  {rec.action}
                </button>
              ))}
            </div>
          </div>

        </div>
      </div>
      
      {/* Footer Timestamp */}
      <div className="bg-black/40 p-2 text-center border-t border-white/5">
        <p className="text-[10px] text-gray-600 font-mono">
          PREDICTION SNAPSHOT GENERATED AT {new Date(metadata.generated_at).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
