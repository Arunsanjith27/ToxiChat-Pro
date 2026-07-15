import React from "react";
import { cn } from "../../lib/utils";

// Stub for a Resizable Panel (could use react-resizable-panels in the future)
export function ResizablePanel({ children, defaultSize, minSize, maxSize, className }) {
  return (
    <div 
      className={cn("flex flex-col h-full", className)}
      style={{ flex: `${defaultSize} ${defaultSize} 0%`, minWidth: minSize, maxWidth: maxSize }}
    >
      {children}
    </div>
  );
}

export function ResizableHandle({ className }) {
  return (
    <div className={cn("w-px bg-border hover:bg-brand-500/50 cursor-col-resize transition-colors shrink-0", className)} />
  );
}

export function ResizablePanelGroup({ children, className }) {
  return (
    <div className={cn("flex h-full w-full", className)}>
      {children}
    </div>
  );
}
