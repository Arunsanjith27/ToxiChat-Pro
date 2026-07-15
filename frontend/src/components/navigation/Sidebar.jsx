import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  Home, MessageSquare, Shield, Activity, FileText, 
  Settings, ChevronLeft, ChevronRight, HelpCircle, 
  Bot, AlertTriangle, Database
} from "lucide-react";
import { cn } from "../../lib/utils";
import { motion, AnimatePresence } from "framer-motion";

const MAIN_NAV = [
  { label: "Dashboard", icon: Home, href: "/admin", exact: true },
  { label: "Chat Client", icon: MessageSquare, href: "/chat" },
  { label: "Incidents", icon: AlertTriangle, href: "/admin/incidents" },
  { label: "Reports", icon: FileText, href: "/admin/reports" },
];

const AI_NAV = [
  { label: "Moderator Copilot", icon: Bot, href: "/admin/copilot" },
  { label: "Evidence Analysis", icon: Database, href: "/admin/evidence" },
  { label: "Telemetry & Health", icon: Activity, href: "/admin/telemetry" },
];

const BOTTOM_NAV = [
  { label: "Settings", icon: Settings, href: "/settings" },
  { label: "Support", icon: HelpCircle, href: "/support" },
];

export function Sidebar({ collapsed, setCollapsed, className }) {
  const location = useLocation();

  const isRouteActive = (href, exact = false) => {
    if (exact) return location.pathname === href;
    return location.pathname.startsWith(href);
  };

  const NavItem = ({ item }) => {
    const active = isRouteActive(item.href, item.exact);
    const Icon = item.icon;

    return (
      <Link
        to={item.href}
        className={cn(
          "flex items-center gap-3 rounded-lg px-3 py-2 transition-colors relative group",
          active 
            ? "bg-brand-500/10 text-brand-400 font-medium" 
            : "text-gray-400 hover:text-gray-100 hover:bg-surfaceHover"
        )}
        title={collapsed ? item.label : undefined}
      >
        <Icon className={cn("h-5 w-5 shrink-0", active ? "text-brand-400" : "text-gray-400 group-hover:text-gray-200")} />
        
        <AnimatePresence>
          {!collapsed && (
            <motion.span
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: "auto" }}
              exit={{ opacity: 0, width: 0 }}
              className="truncate whitespace-nowrap"
            >
              {item.label}
            </motion.span>
          )}
        </AnimatePresence>

        {active && (
          <motion.div
            layoutId="sidebar-active-indicator"
            className="absolute left-0 top-1 bottom-1 w-1 bg-brand-500 rounded-r-full"
          />
        )}
      </Link>
    );
  };

  return (
    <aside
      className={cn(
        "relative hidden lg:flex flex-col border-r border-border bg-surface transition-all duration-300 ease-in-out h-[calc(100vh)] z-30",
        collapsed ? "w-16" : "w-64",
        className
      )}
    >
      <div className="flex h-14 items-center justify-between px-4 border-b border-border shrink-0">
        <Link to="/" className="flex items-center gap-2 overflow-hidden">
          <Shield className="h-6 w-6 text-brand-500 shrink-0" />
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                className="font-bold text-lg text-gray-100 whitespace-nowrap truncate"
              >
                ToxiChat <span className="text-brand-500">Pro</span>
              </motion.span>
            )}
          </AnimatePresence>
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden py-4 px-2 space-y-6">
        
        {/* Main Navigation */}
        <div className="space-y-1">
          {!collapsed && (
            <div className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Main Menu
            </div>
          )}
          {MAIN_NAV.map((item) => (
            <NavItem key={item.label} item={item} />
          ))}
        </div>

        {/* AI & Analytics Navigation (Reserved slots) */}
        <div className="space-y-1">
          {!collapsed && (
            <div className="px-3 mb-2 text-xs font-semibold text-brand-500/70 uppercase tracking-wider">
              AI Intelligence
            </div>
          )}
          {AI_NAV.map((item) => (
            <NavItem key={item.label} item={item} />
          ))}
        </div>

      </div>

      {/* Bottom Navigation */}
      <div className="p-2 border-t border-border space-y-1 bg-surfaceHover/30">
        {BOTTOM_NAV.map((item) => (
          <NavItem key={item.label} item={item} />
        ))}
      </div>

      {/* Collapse Toggle Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-16 flex h-6 w-6 items-center justify-center rounded-full border border-border bg-surface text-gray-400 hover:text-gray-100 shadow-sm transition-colors z-40"
      >
        {collapsed ? <ChevronRight className="h-3.5 w-3.5" /> : <ChevronLeft className="h-3.5 w-3.5" />}
      </button>
    </aside>
  );
}
