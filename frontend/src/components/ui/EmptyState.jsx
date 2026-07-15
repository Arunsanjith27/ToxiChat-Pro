import React from "react";
import { cn } from "../../lib/utils";
import { Inbox } from "lucide-react";

export function EmptyState({ 
  icon: Icon = Inbox, 
  title = "No data found", 
  description, 
  action, 
  className 
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-8 text-center", className)}>
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-surfaceHover mb-4">
        <Icon className="h-8 w-8 text-gray-400" />
      </div>
      <h3 className="text-lg font-semibold text-gray-200">{title}</h3>
      {description && (
        <p className="mt-2 text-sm text-gray-400 max-w-sm">{description}</p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
