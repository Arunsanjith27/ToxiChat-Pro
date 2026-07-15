import React from "react";
import { cn } from "../../lib/utils";
import { Activity, AlertTriangle, CheckCircle2 } from "lucide-react";

export function ModelStatus({ modelName, status = "active", latency, className }) {
  const isHealthy = status.toLowerCase() === "active" || status.toLowerCase() === "healthy";
  const isDegraded = status.toLowerCase() === "degraded";

  return (
    <div className={cn("flex items-center justify-between p-2 rounded-lg border bg-surface", 
      isHealthy ? "border-emerald-500/20" : isDegraded ? "border-amber-500/20" : "border-red-500/20",
      className
    )}>
      <div className="flex items-center gap-2">
        {isHealthy ? (
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
        ) : isDegraded ? (
          <AlertTriangle className="w-4 h-4 text-amber-400" />
        ) : (
          <Activity className="w-4 h-4 text-red-400" />
        )}
        <span className="text-sm font-medium text-gray-200">{modelName}</span>
      </div>
      <div className="flex items-center gap-3">
        {latency && (
          <span className="text-[10px] text-gray-500 font-mono">{latency}ms</span>
        )}
        <span className={cn("text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded",
          isHealthy ? "bg-emerald-500/10 text-emerald-400" : isDegraded ? "bg-amber-500/10 text-amber-400" : "bg-red-500/10 text-red-400"
        )}>
          {status}
        </span>
      </div>
    </div>
  );
}
