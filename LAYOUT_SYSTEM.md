# ToxiChat Pro - Layout Architecture System

This document outlines the layout philosophy, component hierarchy, and navigation architecture built during Sprint 1.5. This serves as the permanent frontend architecture through Version 2.0.

## 1. Layout Philosophy

ToxiChat Pro uses an **Application Shell Architecture** (AppShell). 
Instead of every page redefining its own sidebar, top navigation, and layout constraints, pages are wrapped in a layout primitive that handles all navigation and spacing automatically.

This ensures:
*   **Zero Duplication**: Navigation logic exists in exactly one place.
*   **Predictable Responsiveness**: The shell handles the transition from Desktop Sidebar to Mobile Drawer automatically.
*   **Future Proofing**: When we add new AI modules or Enterprise features, we simply add a link to the `Sidebar.jsx`; we do not need to update 20 different page components.

## 2. Component Hierarchy

### Navigation Components (`src/components/navigation`)
*   `Sidebar.jsx`: The primary vertical navigation menu for desktop. Features collapsible icon-only mode and reserved slots for future AI modules.
*   `TopNav.jsx`: The horizontal bar containing Global Search, AI Status, Theme Toggle, Notifications, and User Menu.
*   `MobileDrawer.jsx`: A Framer Motion slide-over panel that replaces the Sidebar on screens `<1024px`.
*   `CommandPalette.jsx`: A global, keyboard-accessible (Ctrl+K) overlay for rapid navigation.
*   `ThemeToggle.jsx`: Switches between Light, Dark, and System themes.

### Layout Wrappers (`src/components/layout`)
Pages should be wrapped in one of the following root wrappers depending on their domain:

1.  **`AppShell`**: The master wrapper. Contains the Sidebar, TopNav, and Drawer.
2.  **`AdminLayout` / `DashboardLayout`**: Wraps `AppShell` and injects a `PageContainer` with standard max-width and padding. Use this for 90% of pages (settings, reports, telemetry).
3.  **`ChatLayout`**: Wraps `AppShell` but explicitly *removes* padding to allow edge-to-edge full-height interfaces (like a chat application).
4.  **`AuthLayout`**: A standalone wrapper (no AppShell) that centers content on the screen with branding.
5.  **`LandingLayout`**: A standalone wrapper for marketing pages featuring a custom top-nav and footer.

### Layout Primitives
Use these inside your pages to structure content:
*   **`PageContainer`**: Constrains max-width (e.g., `max-w-7xl`).
*   **`PageHeader`**: Standardized title, description, and breadcrumb area.
*   **`Section`**: A visual block of content with an optional title border.
*   **`ResponsiveGrid`**: An easy wrapper for responsive multi-column layouts.
*   **`SplitView`**: A 2-pane layout (Left list, Right detail).

## 3. Theme Architecture

The `ThemeContext` provides `dark`, `light`, and `system` modes.
*   User preference is persisted to `localStorage` (`toxichat_theme`).
*   Tailwind's `darkMode: 'class'` is used. The context provider injects `.dark` or `.light` into the `<html>` root node automatically.
*   System mode utilizes `window.matchMedia('(prefers-color-scheme: dark)')` and listens for OS-level changes in real-time.

## 4. Accessibility & Responsive Behavior

*   **Keyboard Navigation**: The Command Palette (`Ctrl+K`) ensures power users can navigate without a mouse.
*   **Mobile Support**: The Sidebar completely hides on mobile (`hidden lg:flex`), replaced by a hamburger menu that triggers the `MobileDrawer`.
*   **Motion**: Framer Motion is used for the Drawer, User Menu dropdown, and Notification Center to provide a Vercel-like, snappy feel (`duration: 0.15`).

## 5. Migration Strategy for Future Sprints

Currently, existing pages (`App.js`, `ChatLayout.jsx`) are completely untouched. 

In future sprints, to migrate a page to the new architecture:
1.  Remove the bespoke navigation/sidebar code from the legacy page.
2.  Wrap the page content in the appropriate layout primitive (e.g., `<AdminLayout>`).
3.  Inject the new page component into `App.js` routes.

**Example Migration:**
```jsx
// Before
export default function LegacySettings() {
  return (
     <div>
       <OldSidebar />
       <div className="content">
         <h1>Settings</h1>
       </div>
     </div>
  )
}

// After
import { AdminLayout, PageHeader, Section } from "@/components/layout";

export default function NewSettings() {
  return (
    <AdminLayout>
      <PageHeader title="Settings" description="Manage your account" />
      <Section title="Profile">
         {/* Form goes here */}
      </Section>
    </AdminLayout>
  )
}
```
