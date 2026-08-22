import React from 'react'
import { Truck, Fuel, ArrowRight, Gauge, CheckCircle, AlertTriangle, AlertCircle } from 'lucide-react'

export default function FleetStatus() {
  const vehicles = [
    {
      id: 'V023',
      route: 'R07',
      fuel: '38.4 L',
      fuelPercent: 82,
      efficiency: 'HIGH RISK',
      efficiencyLevel: 'risk', // red
      status: 'Delayed Traffic',
    },
    {
      id: 'V011',
      route: 'R03',
      fuel: '24.7 L',
      fuelPercent: 46,
      efficiency: 'OPTIMAL',
      efficiencyLevel: 'optimal', // green
      status: 'On Schedule',
    },
    {
      id: 'V031',
      route: 'R05',
      fuel: '31.2 L',
      fuelPercent: 64,
      efficiency: 'MODERATE',
      efficiencyLevel: 'moderate', // yellow
      status: 'Normal Route',
    },
    {
      id: 'V018',
      route: 'R02',
      fuel: '22.1 L',
      fuelPercent: 38,
      efficiency: 'OPTIMAL',
      efficiencyLevel: 'optimal', // green
      status: 'On Schedule',
    },
    {
      id: 'V042',
      route: 'R09',
      fuel: '35.8 L',
      fuelPercent: 74,
      efficiency: 'MODERATE',
      efficiencyLevel: 'moderate', // yellow
      status: 'Rerouting',
    },
  ]

  const getEfficiencyBadge = (level, label) => {
    switch (level) {
      case 'optimal':
        return (
          <span className="inline-flex items-center gap-1 rounded bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-semibold text-emerald-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
            {label}
          </span>
        )
      case 'moderate':
        return (
          <span className="inline-flex items-center gap-1 rounded bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 text-[10px] font-semibold text-amber-400">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-400"></span>
            {label}
          </span>
        )
      case 'risk':
      default:
        return (
          <span className="inline-flex items-center gap-1 rounded bg-rose-500/10 border border-rose-500/30 px-2 py-0.5 text-[10px] font-semibold text-rose-400">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-400"></span>
            {label}
          </span>
        )
    }
  }

  const getProgressBarColor = (level) => {
    switch (level) {
      case 'optimal':
        return 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]'
      case 'moderate':
        return 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]'
      case 'risk':
      default:
        return 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.5)]'
    }
  }

  return (
    <div className="flex flex-col h-full rounded-xl border border-slate-800/80 bg-slate-900/60 shadow-lg shadow-black/20 backdrop-blur-sm overflow-hidden">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-slate-800/70 px-4 py-2.5 bg-slate-950/40">
        <div className="flex items-center gap-2">
          <Truck className="h-4 w-4 text-emerald-400" />
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            Fleet Status
          </h2>
        </div>
        <span className="text-[11px] font-mono text-slate-400">5 Active Telemetries</span>
      </div>

      {/* Vehicle Rows List */}
      <div className="divide-y divide-slate-800/60 overflow-y-auto max-h-[420px] p-2 space-y-2">
        {vehicles.map((v) => (
          <div
            key={v.id}
            className="rounded-lg border border-slate-800/60 bg-slate-950/40 p-3 hover:border-slate-700/80 transition-all"
          >
            {/* Top row: ID, Route, and Efficiency */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-white tracking-wide">
                  {v.id}
                </span>
                <div className="flex items-center gap-1 text-[11px] text-slate-400">
                  <ArrowRight className="h-3 w-3 text-slate-500" />
                  <span className="font-medium text-slate-300">{v.route}</span>
                </div>
              </div>
              {getEfficiencyBadge(v.efficiencyLevel, v.efficiency)}
            </div>

            {/* Fuel Consumption Metric & Bar */}
            <div className="mt-2.5">
              <div className="flex items-center justify-between text-[10px] text-slate-400">
                <span className="flex items-center gap-1">
                  <Fuel className="h-3 w-3 text-slate-400" />
                  Fuel Consumption
                </span>
                <span className="font-mono font-medium text-slate-200">{v.fuel}</span>
              </div>
              <div className="mt-1 h-1.5 w-full rounded-full bg-slate-800/90 overflow-hidden">
                <div
                  className={`h-full rounded-full ${getProgressBarColor(v.efficiencyLevel)}`}
                  style={{ width: `${v.fuelPercent}%` }}
                />
              </div>
            </div>

            {/* Sub-telemetry Footer */}
            <div className="mt-2 flex items-center justify-between text-[10px] text-slate-500 font-mono">
              <span>Status: <span className="text-slate-400">{v.status}</span></span>
              <span>Load: <span className="text-slate-400">{v.fuelPercent}%</span></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
