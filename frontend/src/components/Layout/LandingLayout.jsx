import React from "react";
import { Link } from "react-router-dom";
import { Shield } from "lucide-react";
import { Button } from "../ui/Button";

export function LandingLayout({ children }) {
  // LandingLayout is a standalone layout with a minimal top navigation bar for marketing pages.
  return (
    <div className="min-h-screen w-full flex flex-col bg-background font-sans text-gray-100 selection:bg-brand-500/30 selection:text-brand-300">
      
      {/* Landing Top Nav */}
      <header className="sticky top-0 z-50 w-full border-b border-border bg-surface/80 backdrop-blur">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <Shield className="h-7 w-7 text-brand-500" />
            <span className="font-bold text-xl tracking-tight text-gray-100">
              ToxiChat <span className="text-brand-500">Pro</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-300">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#ai" className="hover:text-white transition-colors">AI Engine</a>
            <a href="#security" className="hover:text-white transition-colors">Security</a>
          </nav>

          <div className="flex items-center gap-4">
            <Link to="/login" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">
              Log in
            </Link>
            <Button asChild size="sm">
              <Link to="/register">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Marketing Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Standard Footer */}
      <footer className="border-t border-border bg-surface py-12 mt-auto">
        <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2 opacity-50">
            <Shield className="h-5 w-5" />
            <span className="font-bold tracking-tight">ToxiChat Pro</span>
          </div>
          <p className="text-sm text-gray-500">
            &copy; {new Date().getFullYear()} ToxiChat Pro. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
