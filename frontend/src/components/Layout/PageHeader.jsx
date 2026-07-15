import React from "react";
import { cn } from "../../lib/utils";
import { Breadcrumb } from "../navigation/Breadcrumb";

export function PageHeader({ title, description, breadcrumbs, actions, className }) {
  return (
    <div className={cn("flex flex-col gap-4 mb-8", className)}>
      {breadcrumbs && breadcrumbs.length > 0 && (
        <Breadcrumb items={breadcrumbs} />
      )}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-gray-100">{title}</h1>
          {description && (
            <p className="text-gray-400 mt-1 max-w-2xl">{description}</p>
          )}
        </div>
        {actions && (
          <div className="flex items-center gap-2 shrink-0">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
}
