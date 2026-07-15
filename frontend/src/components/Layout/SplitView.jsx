import React from "react";
import { cn } from "../../lib/utils";

export function SplitView({ leftPanel, rightPanel, className, defaultRatio = 30 }) {
  // Hardcoded for now. A real split view might use react-split or drag events.
  return (
    <div className={cn("flex w-full h-full overflow-hidden", className)}>
      <div 
        className="h-full border-r border-border shrink-0" 
        style={{ width: `${defaultRatio}%` }}
      >
        {leftPanel}
      </div>
      <div className="flex-1 h-full min-w-0">
        {rightPanel}
      </div>
    </div>
  );
}
