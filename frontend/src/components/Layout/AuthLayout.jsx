import React from "react";
import { cn } from "../../lib/utils";
import { Shield } from "lucide-react";
import { Link } from "react-router-dom";

export function AuthLayout({ children, title, subtitle }) {
  // AuthLayout is a standalone layout (no AppShell).
  // It centers the authentication form on the screen with branding.
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background p-4 sm:p-8 font-sans selection:bg-brand-500/30 selection:text-brand-300">
      <div className="w-full max-w-md space-y-8">
        {/* Branding Header */}
        <div className="flex flex-col items-center text-center">
          <Link to="/" className="flex items-center gap-2 mb-6">
            <Shield className="h-10 w-10 text-brand-500" />
            <span className="font-bold text-2xl text-gray-100">
              ToxiChat <span className="text-brand-500">Pro</span>
            </span>
          </Link>
          
          {title && <h2 className="text-2xl font-semibold tracking-tight text-gray-100">{title}</h2>}
          {subtitle && <p className="text-sm text-gray-400 mt-2">{subtitle}</p>}
        </div>

        {/* Content Box */}
        <div className="bg-surface border border-border rounded-xl shadow-2xl p-6 sm:p-8">
          {children}
        </div>
      </div>
    </div>
  );
}
