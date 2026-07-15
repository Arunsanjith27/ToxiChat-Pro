import React, { useState } from "react";
import { Sidebar } from "../navigation/Sidebar";
import { TopNav } from "../navigation/TopNav";
import { MobileDrawer } from "../navigation/MobileDrawer";
import { CommandPalette } from "../navigation/CommandPalette";

export function AppShell({ children }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden font-sans text-gray-100 selection:bg-brand-500/30 selection:text-brand-300">
      {/* Global Command Palette */}
      <CommandPalette />
      
      {/* Desktop Sidebar */}
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />
      
      {/* Mobile Drawer */}
      <MobileDrawer isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />
      
      {/* Main Content Area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden relative">
        <TopNav 
          onOpenMobileMenu={() => setMobileMenuOpen(true)} 
          showMobileMenuBtn={true} 
        />
        
        <main className="flex-1 overflow-y-auto overflow-x-hidden relative focus:outline-none" tabIndex="-1">
          {children}
        </main>
      </div>
    </div>
  );
}
