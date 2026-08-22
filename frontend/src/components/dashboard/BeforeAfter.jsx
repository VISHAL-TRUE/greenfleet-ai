import React from 'react'
import { Scale, ArrowDownRight, ArrowUpRight, CheckCircle2 } from 'lucide-react'

export default function BeforeAfter() {
  const comparisonRows = [
    {
      metric: 'Fuel Consumption',
      baseline: '1,842 L',
      greenflow: '1,497 L',
      delta: '-345 L (-18.7%)',
      isImprovement: true,
      baselinePercent: 100,
      greenflowPercent: 81.3,
    },
    {
      metric: 'Estimated CO₂ Emissions',
      baseline: '4.8 t',
      greenflow: '3.9 t',
      delta: '-0.9 t (-18.8%)',
      isImprovement: true,
      baselinePercent: 100,
      greenflowPercent: 81.2,
    },
    {
      metric: 'Total Operating Cost',
      baseline: '₹31,400',
      greenflow: '₹26,900',
      delta: '-₹4,500 (-14.3%)',
      isImprovement: true,
      baselinePercent: 100,
      greenflowPercent: 85.7,
    },
    {
      metric: 'Fleet Utilisation Rate',
      baseline: '71%',
      greenflow: '87%',
      delta: '+16.0%',
      isImprovement: true,
      baselinePercent: 71,
      greenflowPercent: 87,
    },
  ]

  return (
    <div className="flex flex-col rounded-xl border border-slate-800/80 bg-slate-900/60 shadow-lg shadow-black/20 backdrop-blur-sm overflow-hidden">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-slate-800/70 px-4 py-2.5 bg-slate-950/40">
        <div className="flex items-center gap-2">
          <Scale className="h-4 w-4 text-emerald-400" />
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            Baseline vs GreenFlow
          </h2>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>Optimisation Verified</span>
        </div>
      </div>

      {/* Comparison Table / Grid */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800/60 bg-slate-950/30 text-[10px] uppercase font-semibold text-slate-400 tracking-wider">
              <th className="py-2.5 px-4">Metric</th>
              <th className="py-2.5 px-4 text-right">Baseline</th>
              <th className="py-2.5 px-4 text-right">GreenFlow AI</th>
              <th className="py-2.5 px-4 text-right">Impact / Delta</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50 font-mono">
            {comparisonRows.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-3 px-4 font-sans font-medium text-slate-200 text-xs">
                  {row.metric}
                </td>
                <td className="py-3 px-4 text-right text-slate-400">
                  {row.baseline}
                </td>
                <td className="py-3 px-4 text-right font-bold text-white">
                  <span className="inline-block rounded bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 text-emerald-300">
                    {row.greenflow}
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <span className="inline-flex items-center gap-1 font-semibold text-emerald-400 text-xs">
                    <ArrowDownRight className="h-3.5 w-3.5" />
                    {row.delta}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
