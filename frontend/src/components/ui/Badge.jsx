import React from "react";
import { cn } from "../../lib/utils";

const badgeVariants = {
  default: "bg-brand-500/20 text-brand-400 border-brand-500/30",
  secondary: "bg-surfaceHover text-gray-300 border-border",
  destructive: "bg-red-500/20 text-red-400 border-red-500/30",
  warning: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  outline: "text-gray-100 border-border",
  ai: "bg-indigo-500/20 text-indigo-400 border-indigo-500/30",
};

export function Badge({ className, variant = "default", ...props }) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2",
        badgeVariants[variant],
        className
      )}
      {...props}
    />
  );
}
