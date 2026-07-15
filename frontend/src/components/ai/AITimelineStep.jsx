import React from "react";
import { cn } from "../../lib/utils";
import { Check, Loader2, X } from "lucide-react";

export function AITimelineStep({ 
  stepName, 
  status = "pending", // pending, processing, success, error
  description,
  isLast = false,
  className
}) {
  return (
    <div className={cn("relative flex gap-4 pb-6", isLast && "pb-0", className)}>
      {/* Line connecting steps */}
      {!isLast && (
        <div className={cn(
          "absolute left-3 top-8 bottom-0 w-px -translate-x-1/2",
          status === "success" ? "bg-brand-500/50" : "bg-border"
        )} />
      )}

      {/* Icon */}
      <div className={cn(
        "relative z-10 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-xs font-medium",
        status === "success" ? "bg-brand-500/20 border-brand-500/50 text-brand-400" :
        status === "error" ? "bg-red-500/20 border-red-500/50 text-red-400" :
        status === "processing" ? "bg-indigo-500/20 border-indigo-500/50 text-indigo-400" :
        "bg-surfaceHover border-border text-gray-500"
      )}>
        {status === "success" ? <Check className="h-3 w-3" /> :
         status === "error" ? <X className="h-3 w-3" /> :
         status === "processing" ? <Loader2 className="h-3 w-3 animate-spin" /> :
         <span className="h-1.5 w-1.5 rounded-full bg-gray-500" />}
      </div>

      {/* Content */}
      <div className="flex flex-col pt-0.5">
        <span className={cn(
          "text-sm font-semibold",
          status === "pending" ? "text-gray-500" : "text-gray-200"
        )}>
          {stepName}
        </span>
        {description && (
          <span className="text-xs text-gray-400 mt-1">{description}</span>
        )}
      </div>
    </div>
  );
}
