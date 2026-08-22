import React from 'react'
import { MapPin, Navigation, Compass, Layers, ShieldCheck } from 'lucide-react'

export default function FleetMapPlaceholder() {
  return (
    <div className="flex flex-col h-full rounded-xl border border-slate-800/80 bg-slate-900/60 shadow-lg shadow-black/20 backdrop-blur-sm overflow-hidden">
      {/* Map Header */}
      <div className="flex items-center justify-between border-b border-slate-800/70 px-4 py-2.5 bg-slate-950/40">
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-emerald-400" />
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            Fleet & Route Network
          </h2>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[11px] font-medium">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></span>
            <span className="text-slate-300">Optimal</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.6)]"></span>
            <span className="text-slate-300">Moderate</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]"></span>
            <span className="text-slate-300">High Risk</span>
          </div>
        </div>
      </div>

      {/* Map Canvas Placeholder */}
      <div className="relative flex-1 min-h-[380px] bg-[#070b13] flex items-center justify-center overflow-hidden select-none">
        {/* Subtle Map Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.08) 0%, transparent 60%),
              linear-gradient(to right, #1e293b 1px, transparent 1px),
              linear-gradient(to bottom, #1e293b 1px, transparent 1px)
            `,
            backgroundSize: '100% 100%, 40px 40px, 40px 40px',
          }}
        />

        {/* Mock Route Lines SVG Overlay */}
        <svg className="absolute inset-0 h-full w-full pointer-events-none opacity-40">
          <defs>
            <linearGradient id="routeGradientGreen" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#065f46" stopOpacity="0.2" />
            </linearGradient>
            <linearGradient id="routeGradientAmber" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#78350f" stopOpacity="0.2" />
            </linearGradient>
          </defs>
          {/* Path 1 */}
          <path
            d="M 120 180 Q 260 90 420 160 T 680 240"
            fill="none"
            stroke="url(#routeGradientGreen)"
            strokeWidth="2"
            strokeDasharray="4 4"
          />
          {/* Path 2 */}
          <path
            d="M 180 300 Q 340 360 520 280 T 780 180"
            fill="none"
            stroke="url(#routeGradientAmber)"
            strokeWidth="2"
            strokeDasharray="5 3"
          />
          {/* Path 3 */}
          <path
            d="M 280 120 L 500 210 L 620 340"
            fill="none"
            stroke="#10b981"
            strokeWidth="1.5"
            strokeOpacity="0.4"
          />
        </svg>

        {/* Visual Route Nodes / Markers */}
        <div className="absolute top-[22%] left-[28%] flex flex-col items-center">
          <span className="relative flex h-4 w-4 items-center justify-center">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60"></span>
            <span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-500 border border-emerald-300"></span>
          </span>
          <span className="mt-1 rounded bg-slate-900/90 border border-slate-700/80 px-1.5 py-0.5 text-[9px] font-mono text-emerald-300 shadow-md">
            Hub North • V011
          </span>
        </div>

        <div className="absolute top-[48%] left-[54%] flex flex-col items-center">
          <span className="relative flex h-4 w-4 items-center justify-center">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-60"></span>
            <span className="relative inline-flex h-3 w-3 rounded-full bg-amber-500 border border-amber-300"></span>
          </span>
          <span className="mt-1 rounded bg-slate-900/90 border border-slate-700/80 px-1.5 py-0.5 text-[9px] font-mono text-amber-300 shadow-md">
            Central Depot • V031
          </span>
        </div>

        <div className="absolute bottom-[28%] right-[22%] flex flex-col items-center">
          <span className="relative flex h-4 w-4 items-center justify-center">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-400 opacity-60"></span>
            <span className="relative inline-flex h-3 w-3 rounded-full bg-rose-500 border border-rose-300"></span>
          </span>
          <span className="mt-1 rounded bg-slate-900/90 border border-slate-700/80 px-1.5 py-0.5 text-[9px] font-mono text-rose-300 shadow-md">
            Corridor South • V023
          </span>
        </div>

        {/* Center Empty State / Placeholder Banner */}
        <div className="relative z-10 flex flex-col items-center rounded-xl border border-slate-800/90 bg-slate-950/85 px-6 py-4 text-center shadow-xl backdrop-blur-md max-w-sm">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-2.5">
            <Navigation className="h-5 w-5" />
          </div>
          <span className="text-xs font-semibold text-slate-200">Interactive Map Viewport</span>
          <p className="mt-1 text-[11px] text-slate-400 leading-relaxed">
            Geospatial route network ready for Leaflet layer integration and live GPS telemetry.
          </p>
        </div>

        {/* Map UI Floating Controls Placeholder */}
        <div className="absolute top-3 right-3 flex flex-col gap-1.5 z-10">
          <div className="flex h-7 w-7 items-center justify-center rounded-md border border-slate-800 bg-slate-900/80 text-slate-300 shadow-sm text-xs font-bold hover:bg-slate-800 cursor-pointer">
            +
          </div>
          <div className="flex h-7 w-7 items-center justify-center rounded-md border border-slate-800 bg-slate-900/80 text-slate-300 shadow-sm text-xs font-bold hover:bg-slate-800 cursor-pointer">
            -
          </div>
        </div>

        {/* Bottom Attribution Placeholder */}
        <div className="absolute bottom-2 right-2 rounded bg-slate-950/80 border border-slate-800/80 px-2 py-0.5 text-[9px] font-mono text-slate-500">
          Leaflet | © OpenStreetMap contributors
        </div>
      </div>
    </div>
  )
}
