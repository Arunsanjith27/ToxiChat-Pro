import React from "react";
import { cn } from "../../lib/utils";

const variantClasses = {
  default: "bg-brand-500 text-white hover:bg-brand-600 shadow-sm",
  destructive: "bg-red-500 text-white hover:bg-red-600 shadow-sm",
  outline: "border border-border bg-transparent hover:bg-surfaceHover text-gray-200",
  secondary: "bg-surfaceHover text-gray-100 hover:bg-surface border border-border shadow-sm",
  ghost: "hover:bg-surfaceHover text-gray-200 hover:text-white",
  link: "text-brand-500 underline-offset-4 hover:underline",
};

const sizeClasses = {
  default: "h-9 px-4 py-2",
  sm: "h-8 rounded-md px-3 text-xs",
  lg: "h-10 rounded-md px-8",
  icon: "h-9 w-9",
};

export const Button = React.forwardRef(
  ({ className, variant = "default", size = "default", asChild = false, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled}
        className={cn(
          "inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-brand-500 disabled:pointer-events-none disabled:opacity-50",
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";
