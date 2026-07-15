import React, { useState, useRef, useEffect } from "react";
import { Bell } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "../../lib/utils";
import { Button } from "../ui/Button";

export function NotificationCenter({ className }) {
  const [isOpen, setIsOpen] = useState(false);
  const [hasUnread, setHasUnread] = useState(true); // Mock state
  const menuRef = useRef(null);

  // Close menu on click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className={cn("relative", className)} ref={menuRef}>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => {
          setIsOpen(!isOpen);
          setHasUnread(false);
        }}
        aria-label="Notifications"
        aria-expanded={isOpen}
        className="relative"
      >
        <Bell className="h-5 w-5 text-gray-400" />
        {hasUnread && (
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-brand-500 ring-2 ring-surface" />
        )}
      </Button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-2 w-80 rounded-xl border border-border bg-surface shadow-2xl py-2 z-50 origin-top-right overflow-hidden flex flex-col max-h-[400px]"
          >
            <div className="px-4 py-2 border-b border-border flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-100">Notifications</h3>
              <button className="text-xs text-brand-400 hover:text-brand-300 transition-colors">
                Mark all as read
              </button>
            </div>
            
            <div className="overflow-y-auto flex-1 p-2 space-y-1">
              {/* Mock Notification Item */}
              <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-surfaceHover transition-colors cursor-pointer">
                <div className="h-8 w-8 rounded-full bg-brand-500/20 flex items-center justify-center shrink-0 mt-0.5">
                  <Bell className="h-4 w-4 text-brand-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-200 font-medium">Welcome to ToxiChat Pro</p>
                  <p className="text-xs text-gray-400 mt-0.5 line-clamp-2">
                    Your moderation environment is ready. Configure your AI rules in the admin dashboard.
                  </p>
                  <p className="text-[10px] text-gray-500 mt-1">Just now</p>
                </div>
              </div>
              
              {/* Mock Empty State */}
              <div className="py-8 text-center hidden">
                <Bell className="h-8 w-8 text-gray-600 mx-auto mb-2" />
                <p className="text-sm text-gray-400">No new notifications</p>
              </div>
            </div>
            
            <div className="px-4 py-2 border-t border-border bg-surfaceHover/50">
              <button className="text-xs text-gray-300 w-full text-center hover:text-white transition-colors">
                View all notifications
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
