import React from "react";
import { cn } from "../../lib/utils";
import { Loader2 } from "lucide-react";

export function Loader({ className, size = "default", text }) {
  const sizeClasses = {
    sm: "w-4 h-4",
    default: "w-6 h-6",
    lg: "w-8 h-8",
    xl: "w-12 h-12",
  };

  return (
    <div className={cn("flex flex-col items-center justify-center gap-2 text-gray-400", className)}>
      <Loader2 className={cn("animate-spin text-brand-500", sizeClasses[size])} />
      {text && <span className="text-sm font-medium">{text}</span>}
    </div>
  );
}
