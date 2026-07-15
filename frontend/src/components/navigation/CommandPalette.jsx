import React, { useState, useEffect } from "react";
import { Search, Settings, Home, MessageSquare, Shield, Activity } from "lucide-react";
import { Modal } from "../ui/Modal";
import { Input } from "../ui/Input";

const MOCK_COMMANDS = [
  { id: 1, name: "Go to Dashboard", icon: Home, shortcut: "G D" },
  { id: 2, name: "Go to Chat", icon: MessageSquare, shortcut: "G C" },
  { id: 3, name: "Go to Admin", icon: Shield, shortcut: "G A" },
  { id: 4, name: "View Telemetry", icon: Activity, shortcut: "G T" },
  { id: 5, name: "Settings", icon: Settings, shortcut: "G S" },
];

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Toggle on Ctrl+K or Cmd+K
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen((open) => !open);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  const filteredCommands = MOCK_COMMANDS.filter((cmd) => 
    cmd.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      showClose={false}
      className="max-w-xl bg-surface/95 backdrop-blur shadow-2xl overflow-hidden p-0"
    >
      <div className="flex items-center px-4 py-3 border-b border-border">
        <Search className="h-5 w-5 text-gray-400 mr-3 shrink-0" />
        <input
          autoFocus
          className="flex-1 bg-transparent border-0 outline-none text-gray-100 placeholder:text-gray-500"
          placeholder="Type a command or search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <kbd className="hidden sm:inline-flex items-center gap-1 px-1.5 font-mono text-[10px] font-medium text-gray-400 bg-surfaceHover rounded border border-border">
          ESC
        </kbd>
      </div>

      <div className="max-h-[300px] overflow-y-auto p-2">
        {filteredCommands.length === 0 ? (
          <div className="py-8 text-center text-sm text-gray-400">
            No results found.
          </div>
        ) : (
          <div className="space-y-1">
            {filteredCommands.map((cmd) => (
              <button
                key={cmd.id}
                onClick={() => setIsOpen(false)}
                className="w-full flex items-center justify-between px-3 py-2 text-sm text-gray-200 hover:bg-brand-500/10 hover:text-brand-400 rounded-lg transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <cmd.icon className="h-4 w-4 text-gray-400 group-hover:text-brand-400 transition-colors" />
                  <span>{cmd.name}</span>
                </div>
                {cmd.shortcut && (
                  <span className="text-[10px] tracking-widest text-gray-500 font-mono">
                    {cmd.shortcut}
                  </span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </Modal>
  );
}
