import React from 'react'
import { BarChart3, LineChart, TrendingUp, Zap, Gauge } from 'lucide-react'

export default function AnalyticsPlaceholder() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-3.5">
      {/* Panel 1: Fuel Consumption Analysis */}
      <div className="flex flex-col rounded-xl border border-slate-800/80 bg-slate-900/60 shadow-lg shadow-black/20 backdrop-blur-sm overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-800/70 px-4 py-2.5 bg-slate-950/40">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-emerald-400" />
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
              Fuel Consumption Analysis
            </h2>
          </div>
          <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-sm bg-slate-600"></span> Baseline
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-sm bg-emerald-500"></span> GreenFlow
            </span>
          </div>
        </div>

        {/* Visual Chart Placeholder Body */}
        <div className="p-4 flex flex-col justify-between h-[200px] bg-slate-950/20">
          <div className="flex items-end justify-between gap-3 h-[140px] pt-4 px-2 border-b border-slate-800/80">
            {/* Y Axis Guides */}
            <div className="flex flex-col justify-between h-full text-[9px] font-mono text-slate-400 pr-2 select-none">
              <span>60 L</span>
              <span>40 L</span>
              <span>20 L</span>
              <span>0 L</span>
            </div>

            {/* Mock Bars */}
            {[
              { id: 'R01', base: 65, opt: 48, color: 'bg-emerald-500' },
              { id: 'R02', base: 80, opt: 58, color: 'bg-emerald-500' },
              { id: 'R03', base: 45, opt: 32, color: 'bg-emerald-500' },
              { id: 'R04', base: 90, opt: 72, color: 'bg-amber-500' },
              { id: 'R05', base: 70, opt: 52, color: 'bg-emerald-500' },
              { id: 'R06', base: 55, opt: 40, color: 'bg-emerald-500' },
              { id: 'R07', base: 85, opt: 68, color: 'bg-amber-500' },
            ].map((bar) => (
              <div key={bar.id} className="flex-1 flex flex-col items-center gap-1 h-full justify-end group">
                <div className="w-full max-w-[28px] flex items-end justify-center gap-1 h-full">
                  {/* Baseline bar (grey/slate) */}
                  <div
                    className="w-1/2 rounded-t bg-slate-700/60 transition-all group-hover:bg-slate-600"
                    style={{ height: `${bar.base}%` }}
                    title={`Baseline: ${bar.base}L`}
                  />
                  {/* GreenFlow bar (green/amber) */}
                  <div
                    className={`w-1/2 rounded-t ${bar.color} transition-all opacity-90 group-hover:opacity-100 shadow-[0_0_8px_rgba(16,185,129,0.3)]`}
                    style={{ height: `${bar.opt}%` }}
                    title={`Optimized: ${bar.opt}L`}
                  />
                </div>
                <span className="text-[10px] font-mono text-slate-400">{bar.id}</span>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between pt-2 text-[10px] text-slate-400 font-mono">
            <span>Model: Quantum Annealing Hybrid</span>
            <span className="text-emerald-400 font-semibold">Avg Reduction: 18.7%</span>
          </div>
        </div>
      </div>

      {/* Panel 2: Fleet Efficiency */}
      <div className="flex flex-col rounded-xl border border-slate-800/80 bg-slate-900/60 shadow-lg shadow-black/20 backdrop-blur-sm overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-800/70 px-4 py-2.5 bg-slate-950/40">
          <div className="flex items-center gap-2">
            <LineChart className="h-4 w-4 text-emerald-400" />
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
              Fleet Efficiency
            </h2>
          </div>
          <span className="rounded bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 text-[10px] font-mono text-blue-400">
            Target: 85%+
          </span>
        </div>

        {/* Visual Chart Placeholder Body */}
        <div className="p-4 flex flex-col justify-between h-[200px] bg-slate-950/20">
          {/* Visual distribution curves / bars */}
          <div className="flex items-end justify-between gap-3 h-[140px] pt-4 px-2 border-b border-slate-800/80">
            <div className="flex flex-col justify-between h-full text-[9px] font-mono text-slate-400 pr-2 select-none">
              <span>100%</span>
              <span>75%</span>
              <span>50%</span>
              <span>25%</span>
            </div>

            {[
              { route: 'Hub N', score: 94, state: 'bg-emerald-500', eta: '42 min' },
              { route: 'Hub S', score: 88, state: 'bg-emerald-500', eta: '36 min' },
              { route: 'Depot E', score: 91, state: 'bg-emerald-500', eta: '50 min' },
              { route: 'Depot W', score: 76, state: 'bg-amber-500', eta: '68 min' },
              { route: 'Metro C', score: 85, state: 'bg-emerald-500', eta: '29 min' },
              { route: 'Express', score: 96, state: 'bg-emerald-500', eta: '22 min' },
            ].map((item, idx) => (
              <div key={idx} className="flex-1 flex flex-col items-center gap-1 h-full justify-end group">
                <div className="w-full max-w-[22px] flex items-end justify-center h-full">
                  <div
                    className={`w-full rounded-t ${item.state} opacity-85 group-hover:opacity-100 transition-all shadow-[0_0_8px_rgba(16,185,129,0.3)]`}
                    style={{ height: `${item.score}%` }}
                  />
                </div>
                <span className="text-[9px] font-mono text-slate-400 truncate max-w-[45px] text-center">
                  {item.route}
                </span>
              </div>
            ))}
          </div>

          {/* Sub status summary pills */}
          <div className="flex items-center justify-between pt-2 text-[10px] text-slate-400 font-mono">
            <div className="flex items-center gap-3">
              <span className="text-emerald-400 font-medium">Optimal: 5 Clusters</span>
              <span className="text-amber-400 font-medium">Moderate: 1 Cluster</span>
            </div>
            <span className="text-slate-400">Score Index: 89.2</span>
          </div>
        </div>
      </div>
    </div>
  )
}
