import React from "react";
import { cn } from "../../lib/utils";
import { Brain } from "lucide-react";

export function ConfidenceMeter({ confidence = 0, className }) {
  const normalizedConfidence = Math.max(0, Math.min(100, confidence * 100));

  const getColor = (conf) => {
    if (conf >= 80) return "text-emerald-400";
    if (conf >= 50) return "text-amber-400";
    return "text-red-400";
  };

  return (
    <div className={cn("inline-flex items-center gap-1.5 px-2 py-1 rounded bg-surfaceHover border border-border", className)}>
      <Brain className={cn("w-3.5 h-3.5", getColor(normalizedConfidence))} />
      <span className={cn("text-[10px] font-bold uppercase", getColor(normalizedConfidence))}>
        {normalizedConfidence.toFixed(0)}% Conf
      </span>
    </div>
  );
}
