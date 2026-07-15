# ToxiChat Pro - Design System Foundation

Welcome to the ToxiChat Pro Design System. This document explains the core principles, design tokens, and components available for building the frontend.

## 1. Principles
*   **Professional SaaS:** A clean, uncluttered interface suitable for enterprise tools.
*   **Dark Theme First:** Optimized for long periods of screen time and to make moderation alerts (red, yellow) stand out clearly.
*   **Subtle Animation:** Use animation only to clarify state changes (e.g., loading, AI processing, side panels opening) using Framer Motion.
*   **Consistent Scaling:** All padding, margins, and sizing adhere to an 8px grid (Tailwind's default scale).

## 2. Design Tokens (`tailwind.config.js`)

We use extended Tailwind tokens to maintain consistency.

### Colors
*   `bg-background`: The primary application background (`#0b0f19`).
*   `bg-surface`: The background for cards, modals, and panels (`#111827`).
*   `bg-surfaceHover`: A slightly lighter shade for hovers and secondary panels (`#1f2937`).
*   `border-border`: A standardized subtle border (`rgba(255,255,255,0.1)`).
*   `brand-*`: The primary emerald/teal color used for safe states and primary actions.
*   `toxic-*`: Distinct red/rose colors used for toxic or flagged content.

### Typography
*   **Font Family**: `Inter, sans-serif`. Automatically applied globally via `font-sans`.

### Radius
*   **Buttons/Inputs**: `rounded-lg` (8px).
*   **Cards/Modals**: `rounded-xl` (12px) to feel softer and more modern.

## 3. UI Components (`src/components/ui`)

Reusable, generic UI components built using standard Tailwind classes and the `cn()` utility for easy className overriding.

*   **`Button`**: Supports `variant` (`default`, `destructive`, `outline`, `secondary`, `ghost`, `link`) and `size` (`default`, `sm`, `lg`, `icon`).
*   **`Card`**: Composable interface (`Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`).
*   **`Input`**: Standardized text input with focus states.
*   **`Badge`**: Supports `variant` (`default`, `secondary`, `destructive`, `warning`, `outline`, `ai`).
*   **`Modal`**: Framer-motion powered accessible dialog window.
*   **`Tabs`**: Clean, underline-style tabs.
*   **`Table`**: Composable responsive data table (`Table`, `TableHeader`, `TableBody`, `TableRow`, `TableHead`, `TableCell`).
*   **`Alert`**: System messages supporting `variant` (`default`, `destructive`, `success`, `warning`).
*   **`Loader`**: A standard spinning icon for async operations.
*   **`EmptyState`**: Standardized graphic and text for empty lists/searches.
*   **`FileUpload`**: Drag-and-drop zone.

## 4. AI Components (`src/components/ai`)

Domain-specific components for visualizing ToxiChat's moderation engine.

*   **`RiskMeter`**: A progress-bar style indicator for 0-100% risk scoring.
*   **`ConfidenceMeter`**: A small badge showing the AI's confidence percentage.
*   **`ModelStatus`**: Visual indicator for local AI model health and latency.
*   **`AITimelineStep`**: Used to build a vertical timeline of the 7-stage AI analysis pipeline.

## 5. Animation Utilities (`src/lib/animations.js`)

Centralized Framer Motion variants. Use these to ensure consistent motion across the app.

```javascript
import { motion } from "framer-motion";
import { slideUp } from "@/lib/animations";

<motion.div variants={slideUp} initial="initial" animate="animate" exit="exit">
  Content
</motion.div>
```

Available variants:
*   `fadeIn`
*   `slideUp`
*   `slideInFromRight`
*   `staggerContainer` & `staggerItem`
*   `pulseRing`
