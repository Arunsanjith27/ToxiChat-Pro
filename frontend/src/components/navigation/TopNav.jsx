import React from "react";
import { Search, Menu } from "lucide-react";
import { cn } from "../../lib/utils";
import { UserMenu } from "./UserMenu";
import { NotificationCenter } from "./NotificationCenter";
import { ThemeToggle } from "./ThemeToggle";
import { Button } from "../ui/Button";

export function TopNav({ onOpenMobileMenu, showMobileMenuBtn = false, title }) {
  return (
    <header className="sticky top-0 z-40 flex h-14 w-full items-center justify-between border-b border-border bg-surface/80 backdrop-blur px-4">
      <div className="flex items-center gap-4">
        {showMobileMenuBtn && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onOpenMobileMenu}
            className="lg:hidden -ml-2"
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5 text-gray-200" />
          </Button>
        )}
        
        {/* Optional Page Title injected into top nav for mobile or compact layouts */}
        {title && (
          <h1 className="text-sm font-semibold text-gray-100 lg:hidden truncate max-w-[200px]">
            {title}
          </h1>
        )}

        {/* Global Search Trigger - Desktop */}
        <button 
          className="hidden lg:flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 bg-surfaceHover border border-border rounded-lg hover:border-brand-500/50 hover:text-gray-200 transition-colors w-64 text-left group"
          onClick={() => {
            // Trigger command palette (mock trigger by dispatching keyboard event)
            document.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true }));
          }}
        >
          <Search className="h-4 w-4 shrink-0" />
          <span className="flex-1 truncate">Search...</span>
          <kbd className="hidden sm:inline-flex items-center gap-1 px-1.5 font-mono text-[10px] font-medium text-gray-500 bg-surface rounded border border-border group-hover:text-gray-400 transition-colors">
            Ctrl K
          </kbd>
        </button>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {/* Global Search Trigger - Mobile */}
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          aria-label="Search"
          onClick={() => {
            document.dispatchEvent(new KeyboardEvent('keydown', { key: 'k', ctrlKey: true }));
          }}
        >
          <Search className="h-5 w-5 text-gray-400" />
        </Button>
        
        <div className="hidden sm:flex items-center px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/20 mr-2">
          <span className="flex h-2 w-2 rounded-full bg-brand-500 mr-2 animate-pulse" />
          <span className="text-xs font-semibold text-brand-400 uppercase tracking-wider">AI Pipeline Active</span>
        </div>

        <ThemeToggle />
        <NotificationCenter />
        <div className="h-6 w-px bg-border mx-1" />
        <UserMenu />
      </div>
    </header>
  );
}
