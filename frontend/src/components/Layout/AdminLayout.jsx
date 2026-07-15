import React from "react";
import { AppShell } from "./AppShell";
import { PageContainer } from "./PageContainer";

export function AdminLayout({ children, maxWidth = "7xl" }) {
  // AdminLayout wraps the content in the AppShell and applies a standard PageContainer.
  // This is ideal for most settings, reports, and list views.
  return (
    <AppShell>
      <PageContainer maxWidth={maxWidth}>
        {children}
      </PageContainer>
    </AppShell>
  );
}

// DashboardLayout is an alias for AdminLayout, for semantic clarity when building main dashboards
export const DashboardLayout = AdminLayout;
