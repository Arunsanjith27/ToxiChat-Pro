import React from "react";
import { cn } from "../../lib/utils";

export function Section({ title, description, children, className }) {
  return (
    <section className={cn("space-y-4 mb-8", className)}>
      {(title || description) && (
        <div className="flex flex-col gap-1 border-b border-border pb-3">
          {title && <h2 className="text-lg font-semibold text-gray-100">{title}</h2>}
          {description && <p className="text-sm text-gray-400">{description}</p>}
        </div>
      )}
      <div>{children}</div>
    </section>
  );
}
