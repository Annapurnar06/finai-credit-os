"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Kanban,
  UserCheck,
  Users,
  ChartLine,
  ShieldCheck,
  Gear,
} from "@phosphor-icons/react";

const ICON_MAP = {
  Kanban,
  UserCheck,
  Users,
  ChartLine,
  ShieldCheck,
  Gear,
} as const;

const NAV_ITEMS = [
  { label: "Pipeline", href: "/pipeline", icon: "Kanban" as const },
  { label: "HITL Queue", href: "/hitl-queue", icon: "UserCheck" as const },
  { label: "Borrowers", href: "/borrowers", icon: "Users" as const },
  { label: "Analytics", href: "/analytics", icon: "ChartLine" as const },
  { label: "Policies", href: "/policies", icon: "ShieldCheck" as const },
  { label: "Settings", href: "/settings", icon: "Gear" as const },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 h-screen bg-bg-surface border-r border-border-gold flex flex-col shrink-0">
      <div className="p-6 pb-4">
        <h1 className="font-serif text-2xl text-accent-gold tracking-tight">
          FINAI
        </h1>
        <p className="text-[11px] text-text-tertiary uppercase tracking-[0.15em] mt-0.5">
          Credit OS
        </p>
      </div>

      <nav className="flex-1 px-3 space-y-0.5">
        {NAV_ITEMS.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = ICON_MAP[item.icon];
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded text-[13px] transition-colors duration-150 ${
                isActive
                  ? "text-accent-gold bg-bg-elevated border-l-2 border-accent-gold -ml-px"
                  : "text-text-secondary hover:text-text-primary hover:bg-bg-elevated"
              }`}
            >
              <Icon size={18} weight={isActive ? "fill" : "regular"} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-border-gold">
        <p className="text-[11px] text-text-tertiary">v0.1.0</p>
      </div>
    </aside>
  );
}
