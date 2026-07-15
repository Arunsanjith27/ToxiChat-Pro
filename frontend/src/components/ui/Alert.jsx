import React from "react";
import { cn } from "../../lib/utils";
import { AlertCircle, CheckCircle, Info, AlertTriangle } from "lucide-react";

const alertVariants = {
  default: "bg-surface border-border text-gray-200",
  destructive: "bg-red-500/10 border-red-500/20 text-red-400",
  success: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400",
  warning: "bg-amber-500/10 border-amber-500/20 text-amber-400",
};

const icons = {
  default: Info,
  destructive: AlertCircle,
  success: CheckCircle,
  warning: AlertTriangle,
};

export const Alert = React.forwardRef(({ className, variant = "default", title, children, ...props }, ref) => {
  const Icon = icons[variant];

  return (
    <div
      ref={ref}
      role="alert"
      className={cn(
        "relative w-full rounded-lg border p-4 [&>svg]:absolute [&>svg]:text-foreground [&>svg]:left-4 [&>svg]:top-4 [&>svg+div]:translate-y-[-3px] [&:has(svg)]:pl-11",
        alertVariants[variant],
        className
      )}
      {...props}
    >
      <Icon className="h-5 w-5" />
      {title && <h5 className="mb-1 font-medium leading-none tracking-tight">{title}</h5>}
      <div className="text-sm opacity-90">{children}</div>
    </div>
  );
});
Alert.displayName = "Alert";
