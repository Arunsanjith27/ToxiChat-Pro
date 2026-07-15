import React from "react";
import { cn } from "../../lib/utils";

export function ResponsiveGrid({ children, columns = 3, gap = 4, className }) {
  const colClasses = {
    1: "grid-cols-1",
    2: "grid-cols-1 sm:grid-cols-2",
    3: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3",
    4: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-4",
    5: "grid-cols-1 sm:grid-cols-3 lg:grid-cols-5",
    6: "grid-cols-1 sm:grid-cols-3 lg:grid-cols-6",
  };

  const gapClasses = {
    2: "gap-2",
    4: "gap-4",
    6: "gap-6",
    8: "gap-8",
  };

  return (
    <div className={cn("grid", colClasses[columns], gapClasses[gap], className)}>
      {children}
    </div>
  );
}
