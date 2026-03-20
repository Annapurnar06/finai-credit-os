"use client";

import MockModeIndicator from "../shared/MockModeIndicator";

interface TopBarProps {
  title: string;
  subtitle?: string;
}

export default function TopBar({ title, subtitle }: TopBarProps) {
  const now = new Date();
  const dateStr = now.toLocaleDateString("en-IN", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  return (
    <header className="h-14 bg-bg-surface border-b border-border-gold flex items-center justify-between px-6 shrink-0">
      <div className="flex items-baseline gap-3">
        <h2 className="font-serif text-xl text-text-primary">{title}</h2>
        {subtitle && (
          <span className="text-[11px] text-text-tertiary">{subtitle}</span>
        )}
      </div>

      <div className="flex items-center gap-4">
        <MockModeIndicator />
        <span className="text-[11px] text-text-tertiary font-mono">
          {dateStr}
        </span>
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-bg-elevated border border-border-gold-hover flex items-center justify-center text-[11px] text-accent-gold font-medium">
            CO
          </div>
          <span className="text-[11px] text-text-secondary">
            Credit Officer
          </span>
        </div>
      </div>
    </header>
  );
}
