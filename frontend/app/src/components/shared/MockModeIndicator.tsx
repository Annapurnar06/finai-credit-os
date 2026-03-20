"use client";

import { useEffect, useState } from "react";
import type { HealthResponse } from "@/lib/types";
import { API_BASE } from "@/lib/constants";

export default function MockModeIndicator() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => {});
  }, []);

  if (!health) {
    return (
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono bg-bg-elevated text-text-tertiary border border-border-gold">
          CONNECTING...
        </span>
      </div>
    );
  }

  const isMock = health.llm_mode === "mock";

  return (
    <div className="flex items-center gap-2">
      <span
        className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider border ${
          isMock
            ? "bg-risk-amber-bg text-risk-amber border-risk-amber/20"
            : "bg-risk-green-bg text-risk-green border-risk-green/20"
        }`}
      >
        <span
          className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
            isMock ? "bg-risk-amber" : "bg-risk-green"
          }`}
        />
        {isMock ? "MOCK MODE" : "LIVE"}
      </span>
      <span className="text-[10px] text-text-tertiary font-mono">
        Memory: {health.memory_mode === "in_memory" ? "local" : "mem0"}
      </span>
    </div>
  );
}
