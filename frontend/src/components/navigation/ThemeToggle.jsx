import React from "react";
import { Moon, Sun, Monitor } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";
import { Button } from "../ui/Button";

export function ThemeToggle({ className }) {
  const { theme, setTheme } = useTheme();

  const cycleTheme = () => {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={cycleTheme}
      className={className}
      aria-label="Toggle theme"
      title={`Current theme: ${theme}. Click to change.`}
    >
      {theme === 'light' && <Sun className="h-5 w-5" />}
      {theme === 'dark' && <Moon className="h-5 w-5" />}
      {theme === 'system' && <Monitor className="h-5 w-5" />}
    </Button>
  );
}
