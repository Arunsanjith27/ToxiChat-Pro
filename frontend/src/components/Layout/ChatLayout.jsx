import React from "react";
import { AppShell } from "./AppShell";
import { cn } from "../../lib/utils";

export function ChatLayout({ children, className }) {
  // ChatLayout removes the PageContainer padding to allow full-height edge-to-edge content.
  // Ideal for split views where the chat list is on the left and the message window is on the right.
  return (
    <AppShell>
      <div className={cn("flex flex-col h-full w-full overflow-hidden", className)}>
        {children}
      </div>
    </AppShell>
  );
}
