import React from "react";
import { cn } from "../../lib/utils";

export function PageContainer({ children, className, maxWidth = "7xl" }) {
  const maxWidthClasses = {
    "3xl": "max-w-3xl",
    "4xl": "max-w-4xl",
    "5xl": "max-w-5xl",
    "6xl": "max-w-6xl",
    "7xl": "max-w-7xl",
    "full": "max-w-full",
  };

  return (
    <div className={cn("mx-auto w-full px-4 sm:px-6 lg:px-8 py-6", maxWidthClasses[maxWidth], className)}>
      {children}
    </div>
  );
}
