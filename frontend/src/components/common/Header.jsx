import React from 'react'
import { Cpu, LayoutDashboard, Radio } from 'lucide-react'

export default function Header() {
  return (
    <header className="sticky top-0 z-50 flex h-14 w-full items-center justify-between border-b border-slate-800/80 bg-slate-950/90 px-5 backdrop-blur-md">
      {/* Left: Branding */}
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
          <Cpu className="h-4.5 w-4.5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-base font-bold tracking-tight text-white">
              GreenFleet <span className="text-emerald-400">AI</span>
            </span>
            <span className="rounded bg-emerald-500/10 px-1.5 py-0.5 text-[9px] font-semibold text-emerald-400 border border-emerald-500/20 uppercase tracking-wide">
              Operator v1.0
            </span>
          </div>
          <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400">
            Quantum-Inspired Fleet Optimisation
          </p>
        </div>
      </div>

      {/* Center: Navigation Pill */}
      <div className="flex items-center rounded-lg border border-slate-800 bg-slate-900/80 p-1">
        <button
          type="button"
          className="flex items-center gap-2 rounded-md bg-emerald-500/15 border border-emerald-500/30 px-3 py-1 text-xs font-semibold text-emerald-300 shadow-sm transition-all"
        >
          <LayoutDashboard className="h-3.5 w-3.5" />
          <span>Operator Dashboard</span>
        </button>
      </div>

      {/* Right: System Status */}
      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/60 px-3 py-1 text-xs text-slate-300">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
          </span>
          <span className="text-[11px] font-medium text-slate-300">System Connected</span>
        </div>
      </div>
    </header>
  )
}
