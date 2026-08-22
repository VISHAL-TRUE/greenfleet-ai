import React from 'react'

export default function MetricCard({
  label,
  value,
  unit,
  icon: Icon,
  trend,
  trendPositive = true,
  subtitle,
  accent = 'emerald',
}) {
  const accentStyles = {
    emerald: {
      border: 'border-slate-800/80 hover:border-emerald-500/40',
      iconBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      valueColor: 'text-white',
    },
    blue: {
      border: 'border-slate-800/80 hover:border-blue-500/40',
      iconBg: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      valueColor: 'text-white',
    },
    amber: {
      border: 'border-slate-800/80 hover:border-amber-500/40',
      iconBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      valueColor: 'text-white',
    },
    cyan: {
      border: 'border-slate-800/80 hover:border-cyan-500/40',
      iconBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
      valueColor: 'text-white',
    },
  }

  const currentAccent = accentStyles[accent] || accentStyles.emerald

  return (
    <div
      className={`relative flex items-center justify-between rounded-xl border bg-slate-900/60 p-3.5 shadow-md shadow-black/20 backdrop-blur-sm transition-all duration-200 ${currentAccent.border}`}
    >
      <div className="flex flex-col">
        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          {label}
        </span>
        <div className="mt-1 flex items-baseline gap-1.5">
          <span className={`text-2xl font-bold tracking-tight ${currentAccent.valueColor}`}>
            {value}
          </span>
          {unit && (
            <span className="text-xs font-medium text-slate-400">
              {unit}
            </span>
          )}
        </div>
        {(trend || subtitle) && (
          <div className="mt-1 flex items-center gap-1.5 text-[11px]">
            {trend && (
              <span
                className={`font-semibold ${
                  trendPositive ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {trend}
              </span>
            )}
            {subtitle && (
              <span className="text-slate-400">{subtitle}</span>
            )}
          </div>
        )}
      </div>

      {Icon && (
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border ${currentAccent.iconBg}`}>
          <Icon className="h-5 w-5" />
        </div>
      )}
    </div>
  )
}
