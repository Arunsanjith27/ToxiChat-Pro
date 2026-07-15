import React, { useState } from "react";
import { cn } from "../../lib/utils";

export function Tabs({ tabs, defaultTab, onChange, className }) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);

  const handleTabClick = (tabId) => {
    setActiveTab(tabId);
    onChange?.(tabId);
  };

  return (
    <div className={cn("w-full", className)}>
      <div className="flex items-center space-x-1 border-b border-border mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.id)}
            className={cn(
              "px-4 py-2 text-sm font-medium transition-colors relative border-b-2",
              activeTab === tab.id
                ? "text-brand-400 border-brand-500 bg-brand-500/10 rounded-t-lg"
                : "text-gray-400 border-transparent hover:text-gray-200 hover:bg-surfaceHover rounded-t-lg"
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div>
        {tabs.find((t) => t.id === activeTab)?.content}
      </div>
    </div>
  );
}
