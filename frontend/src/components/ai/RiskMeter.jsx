import React from "react";
import { cn } from "../../lib/utils";

export function RiskMeter({ score = 0, level = "LOW", className }) {
  const normalizedScore = Math.max(0, Math.min(100, score));

  const getColor = (level) => {
    switch (level?.toUpperCase()) {
      case "LOW":
        return "bg-emerald-500";
      case "MEDIUM":
        return "bg-amber-500";
      case "HIGH":
      case "CRITICAL":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getTextColor = (level) => {
    switch (level?.toUpperCase()) {
      case "LOW":
        return "text-emerald-400";
      case "MEDIUM":
        return "text-amber-400";
      case "HIGH":
      case "CRITICAL":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  return (
    <div className={cn("w-full", className)}>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Risk Level</span>
        <span className={cn("text-xs font-bold uppercase", getTextColor(level))}>
          {level} ({normalizedScore}%)
        </span>
      </div>
      <div className="h-2 w-full bg-surfaceHover rounded-full overflow-hidden">
        <div
          className={cn("h-full transition-all duration-500 rounded-full", getColor(level))}
          style={{ width: `${normalizedScore}%` }}
        />
      </div>
    </div>
  );
}
