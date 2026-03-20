"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Eye, EyeSlash } from "@phosphor-icons/react";

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    router.push("/pipeline");
  };

  return (
    <div className="flex h-screen">
      {/* Left — Brand Panel */}
      <div className="flex-1 bg-bg-primary relative flex flex-col items-center justify-center overflow-hidden">
        {/* Hexagonal grid pattern */}
        <svg
          className="absolute inset-0 w-full h-full opacity-[0.03]"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <pattern
              id="hex"
              width="56"
              height="100"
              patternUnits="userSpaceOnUse"
              patternTransform="scale(1.5)"
            >
              <path
                d="M28 66L0 50L0 16L28 0L56 16L56 50L28 66L28 100"
                fill="none"
                stroke="#C8A862"
                strokeWidth="0.5"
              />
              <path
                d="M28 0L28 34L0 50L0 84L28 100L56 84L56 50L28 34"
                fill="none"
                stroke="#C8A862"
                strokeWidth="0.5"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#hex)" />
        </svg>

        <div className="relative z-10 text-center">
          <h1 className="font-serif text-5xl text-accent-gold">FINAI</h1>
          <p className="text-[14px] text-text-secondary uppercase tracking-[0.2em] mt-1">
            Credit OS
          </p>
          <p className="text-[13px] text-text-tertiary mt-6 max-w-[280px]">
            AI-native lending for India&apos;s 560M unserved
          </p>

          <div className="mt-8 space-y-2">
            {[
              "100 agents · Full loan lifecycle",
              "DPI-first · RBI compliant by design",
              "Voice-first for rural borrowers",
            ].map((line, i) => (
              <p
                key={i}
                className="text-[11px] text-text-tertiary/60"
                style={{
                  animation: `fade-in 0.5s ease-out ${0.3 + i * 0.2}s both`,
                }}
              >
                {line}
              </p>
            ))}
          </div>
        </div>
      </div>

      {/* Right — Form Panel */}
      <div className="flex-1 bg-bg-surface flex items-center justify-center">
        <form onSubmit={handleSubmit} className="w-full max-w-[360px] px-8">
          <h2 className="font-serif text-[28px] text-text-primary mb-8">
            Sign In
          </h2>

          <div className="space-y-4">
            <div>
              <label className="text-[11px] text-text-tertiary uppercase tracking-[0.05em]">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="officer@finai.in"
                className="w-full mt-1.5 bg-bg-inset border border-border-gold rounded px-3 py-2.5 text-[13px] text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent-gold-muted transition-colors"
              />
            </div>

            <div>
              <label className="text-[11px] text-text-tertiary uppercase tracking-[0.05em]">
                Password
              </label>
              <div className="relative mt-1.5">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-bg-inset border border-border-gold rounded px-3 py-2.5 text-[13px] text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent-gold-muted transition-colors pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-secondary transition-colors"
                >
                  {showPassword ? (
                    <EyeSlash size={16} />
                  ) : (
                    <Eye size={16} />
                  )}
                </button>
              </div>
            </div>
          </div>

          <button
            type="submit"
            className="w-full mt-6 py-2.5 rounded text-[13px] font-medium text-accent-gold border border-accent-gold hover:bg-accent-gold hover:text-bg-primary transition-all duration-150"
          >
            Sign In
          </button>

          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-border-gold" />
            <span className="text-[11px] text-text-tertiary">
              or continue with
            </span>
            <div className="flex-1 h-px bg-border-gold" />
          </div>

          <button
            type="button"
            className="w-full py-2.5 rounded text-[13px] text-text-secondary border border-border-gold-hover hover:bg-bg-elevated transition-colors"
          >
            Sign in with SSO
          </button>

          <p className="text-[11px] text-text-tertiary text-center mt-8">
            FINAI Credit OS v0.1.0 · Contact admin for access
          </p>
        </form>
      </div>
    </div>
  );
}
