import React, { useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  Home, MessageSquare, Shield, Activity, FileText, 
  Settings, HelpCircle, Bot, AlertTriangle, Database, X
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

export function MobileDrawer({ isOpen, onClose }) {
  const location = useLocation();

  // Prevent scrolling when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

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
        onClick={onClose}
        className={cn(
          "flex items-center gap-3 rounded-lg px-3 py-3 transition-colors relative",
          active 
            ? "bg-brand-500/10 text-brand-400 font-medium" 
            : "text-gray-400 hover:text-gray-100 hover:bg-surfaceHover"
        )}
      >
        <Icon className={cn("h-5 w-5 shrink-0", active ? "text-brand-400" : "text-gray-400")} />
        <span className="truncate whitespace-nowrap">{item.label}</span>
      </Link>
    );
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed inset-y-0 left-0 z-50 flex w-72 flex-col bg-surface shadow-2xl lg:hidden"
          >
            <div className="flex h-14 items-center justify-between px-4 border-b border-border shrink-0">
              <Link to="/" onClick={onClose} className="flex items-center gap-2">
                <Shield className="h-6 w-6 text-brand-500 shrink-0" />
                <span className="font-bold text-lg text-gray-100">
                  ToxiChat <span className="text-brand-500">Pro</span>
                </span>
              </Link>
              <button
                onClick={onClose}
                className="p-1 rounded-md text-gray-400 hover:text-gray-100 hover:bg-surfaceHover transition-colors"
                aria-label="Close menu"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto overflow-x-hidden py-4 px-3 space-y-6">
              <div className="space-y-1">
                <div className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Main Menu
                </div>
                {MAIN_NAV.map((item) => (
                  <NavItem key={item.label} item={item} />
                ))}
              </div>

              <div className="space-y-1">
                <div className="px-3 mb-2 text-xs font-semibold text-brand-500/70 uppercase tracking-wider">
                  AI Intelligence
                </div>
                {AI_NAV.map((item) => (
                  <NavItem key={item.label} item={item} />
                ))}
              </div>
            </div>

            <div className="p-3 border-t border-border space-y-1 bg-surfaceHover/30 shrink-0">
              {BOTTOM_NAV.map((item) => (
                <NavItem key={item.label} item={item} />
              ))}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
