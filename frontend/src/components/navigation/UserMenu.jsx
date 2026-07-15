import React, { useState, useRef, useEffect } from "react";
import { User, LogOut, Settings, Shield } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../../context/AuthContext";
import { cn } from "../../lib/utils";
import { fadeIn, slideUp } from "../../lib/animations";

export function UserMenu({ className }) {
  const { user, logout, isAdmin } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
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

  if (!user) return null;

  return (
    <div className={cn("relative", className)} ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-center w-9 h-9 rounded-full bg-surfaceHover border border-border hover:border-brand-500/50 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500"
        aria-label="User menu"
        aria-expanded={isOpen}
      >
        {user.avatar_url ? (
          <img src={user.avatar_url} alt="Avatar" className="w-full h-full rounded-full object-cover" />
        ) : (
          <span className="text-sm font-semibold text-gray-200">
            {user.username.charAt(0).toUpperCase()}
          </span>
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 mt-2 w-56 rounded-xl border border-border bg-surface shadow-2xl py-1 z-50 origin-top-right"
          >
            <div className="px-4 py-3 border-b border-border">
              <p className="text-sm font-medium text-gray-100">{user.display_name || user.username}</p>
              <p className="text-xs text-gray-400 truncate">@{user.username}</p>
            </div>
            
            <div className="py-1">
              <button className="flex w-full items-center px-4 py-2 text-sm text-gray-300 hover:bg-surfaceHover hover:text-white transition-colors">
                <User className="mr-2 h-4 w-4" />
                Profile
              </button>
              <button className="flex w-full items-center px-4 py-2 text-sm text-gray-300 hover:bg-surfaceHover hover:text-white transition-colors">
                <Settings className="mr-2 h-4 w-4" />
                Settings
              </button>
              {isAdmin && (
                <button className="flex w-full items-center px-4 py-2 text-sm text-brand-400 hover:bg-brand-500/10 transition-colors">
                  <Shield className="mr-2 h-4 w-4" />
                  Admin Dashboard
                </button>
              )}
            </div>
            
            <div className="border-t border-border py-1">
              <button
                onClick={() => {
                  setIsOpen(false);
                  logout();
                }}
                className="flex w-full items-center px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Log out
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
