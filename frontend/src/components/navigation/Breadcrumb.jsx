import React from "react";
import { ChevronRight } from "lucide-react";
import { cn } from "../../lib/utils";

export function Breadcrumb({ items, className }) {
  return (
    <nav aria-label="Breadcrumb" className={cn("flex items-center text-sm", className)}>
      <ol className="flex items-center space-x-2">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          
          return (
            <li key={item.label} className="flex items-center">
              {item.href && !isLast ? (
                <a 
                  href={item.href} 
                  className="text-gray-400 hover:text-gray-100 transition-colors"
                >
                  {item.label}
                </a>
              ) : (
                <span className={cn(
                  "font-medium",
                  isLast ? "text-gray-100" : "text-gray-400"
                )}>
                  {item.label}
                </span>
              )}
              
              {!isLast && (
                <ChevronRight className="h-4 w-4 mx-1 text-gray-600" />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
